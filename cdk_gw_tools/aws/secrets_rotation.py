from __future__ import annotations

import json
import logging
import os
import re
from copy import deepcopy
from datetime import datetime
from typing import Union

import jwt
import yaml
from boto3.session import Session
from cdk_proxy_api_client.proxy_api import ApiClient, ProxyClient
from cdk_proxy_api_client.vclusters import VirturalClusters
from compose_x_common.aws import get_assume_role_session
from compose_x_common.compose_x_common import keyisset

if logging.getLogger().hasHandlers():
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

CDK_API_ENDPOINT = os.environ.get("CDK_API_ENDPOINT")
NEW_TOKEN_LIFETIME_IN_SECONDS = int(
    os.environ.get("NEW_TOKEN_LIFETIME_IN_SECONDS", 3660)
)
CENTRAL_FUNCTION_ARN_TO_INVOKE = os.environ.get("GW_ROTATION_MANAGER_FUNCTION_ARN")
if not CENTRAL_FUNCTION_ARN_TO_INVOKE:
    print(
        "No GW_ROTATION_MANAGER_FUNCTION_ARN set. Will attempt talking to GW directly."
    )
if not CENTRAL_FUNCTION_ARN_TO_INVOKE and not CDK_API_ENDPOINT:
    raise OSError(
        "CDK_API_ENDPOINT not set and no GW_ROTATION_MANAGER_FUNCTION_ARN to invoke."
        "One of the two must be set."
    )


def lambda_handler(event, context):
    lambda_session = Session()
    if keyisset("vcluster", event) and keyisset("expiry", event):
        gateway_secret = get_cdk_gw_admin_creds(lambda_session)
        return {
            "token": get_new_token_for_vcluster(
                gateway_secret,
                {
                    "vcluster": event["vcluster"],
                    "username": event.get("username") or event["vcluster"],
                },
                int(event["expiry"]),
                token_only=True,
            )
        }
    else:
        secret_arn = event["SecretId"]
        token = event["ClientRequestToken"]
        step = event["Step"]

        current_value = lambda_session.client("secretsmanager").get_secret_value(
            SecretId=secret_arn, VersionStage="AWSCURRENT"
        )["SecretString"]
        if isinstance(current_value, str):
            try:
                current_value = json.loads(current_value)
                logger.info("Successfully decode JSON value from SecretString")
            except json.JSONDecodeError:
                logger.info(
                    "The secret content is not a valid JSON. Treating as raw/plain string instead."
                )

        if step == "createSecret":
            create_secret(lambda_session, secret_arn, token, current_value)

        elif step == "setSecret":
            pass

        elif step == "testSecret":
            pass

        elif step == "finishSecret":
            finish_secret(lambda_session, secret_arn, token)

        else:
            raise ValueError("Invalid step parameter")


def create_secret(lambda_session: Session, arn, token, current_value):
    """
    Creates the new secret for vcluster and stores in Secret with AWSPENDING stage.
    First, we check that there are no AWSPENDING secret value already in place.
    """
    client = lambda_session.client("secretsmanager")
    try:
        client("secretsmanager").get_secret_value(
            SecretId=arn, VersionId=token, VersionStage="AWSPENDING"
        )
        logger.warning(
            "createSecret: AWSPENDING already set for secret for {} - {}".format(
                arn, token
            )
        )
    except:
        logger.debug("No AWSPENDING secret already set. Clear to proceed.")
        try:
            new_secret_value = new_gateway_vcluster_secret_value(
                current_value, arn, token, lambda_session
            )
            client.put_secret_value(
                SecretId=arn,
                ClientRequestToken=token,
                SecretString=json.dumps(new_secret_value)
                if not isinstance(new_secret_value, str)
                else new_secret_value,
                VersionStages=["AWSPENDING"],
            )
            logger.info(
                "createSecret: Successfully put AWSPENDING stage secret for ARN %s and version %s."
                % (arn, token)
            )
        except client.exceptions.ResourceExistsException as error:
            logger.exception(error)
            logger.error(
                "A previous secret execution used this ClientToken. Must re-rotate the secret afterwards."
            )
        except Exception as error:
            logger.exception(error)
            logger.error(
                "createSecret: Failed to create a new secret for ARN %s and version %s."
                % (arn, token)
            )
            raise


def finish_secret(lambda_session: Session, arn, token):
    """
    Finalizes/Promotes the rotation process by marking the secret version passed in as the AWSCURRENT secret
    from AWSPENDING stage
    """
    # First describe the secret to get the current version
    service_client = lambda_session.client("secretsmanager")
    metadata = service_client.describe_secret(SecretId=arn)
    current_version = None
    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                logger.info(
                    "finishSecret: Version %s already marked as AWSCURRENT for %s"
                    % (version, arn)
                )
                return
            current_version = version
            break

    # Finalize by staging the secret version current
    service_client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
    logger.info(
        "finishSecret: Successfully set AWSCURRENT stage to version %s for secret %s."
        % (token, arn)
    )


def new_gateway_vcluster_secret_value(
    current_value: Union[dict, str],
    secret_arn: str,
    token: str,
    lambda_session: Session,
) -> Union[dict, str]:
    """
    Calls the GW API Enpdoint to generate a new JWT token for the vcluster.
    It will then use the value of the AWSCURRENT secret and replace the content wit the new token.

    If CENTRAL_FUNCTION_ARN_TO_INVOKE is set, invokes that function to perform the token creation
    Else will call GW itself to get the new token

    If the current value is just a string, we replace it as-is.
    If the current value is a dict, we try upate the value of each key, if the old value is found in the dict value
    """
    if isinstance(current_value, dict):
        current_jwt_token = current_value["SASL_PASSWORD"]
        jwt_token_details = get_vcluster_details_from_token(current_jwt_token)
    else:
        jwt_token_details = get_vcluster_details_from_token(current_value)
    logger.info(
        "Token expiry was set to {}".format(
            datetime.utcfromtimestamp(jwt_token_details["exp"]).strftime("%FT%T")
        )
    )
    if CENTRAL_FUNCTION_ARN_TO_INVOKE:
        logger.info("Using Lambda function to get new token.")
        new_jwt_token = get_token_from_central_function(
            lambda_session, jwt_token_details
        )
    else:
        gateway_secret = get_cdk_gw_admin_creds(lambda_session)
        logger.info("Successfully retrieved GW admin credentials")
        try:
            logger.info(
                f"creating token for vcluster - {jwt_token_details['vcluster']} - {jwt_token_details['username']}"
            )

            new_jwt_token = get_new_token_for_vcluster(
                gateway_secret, jwt_token_details, NEW_TOKEN_LIFETIME_IN_SECONDS
            )
        except Exception as error:
            logger.exception(error)
            logger.error(
                "Failed to create a new JWT token for vcluster {}".format(
                    jwt_token_details["vcluster"]
                )
            )
            raise
    if isinstance(current_value, dict):
        new_secret_value = replace_string_in_dict_values(
            current_value,
            current_value["SASL_USERNAME"],
            jwt_token_details["username"],
            True,
        )
        replace_string_in_dict_values(
            new_secret_value, current_value["SASL_PASSWORD"], new_jwt_token
        )
        return new_secret_value
    return new_jwt_token


def get_token_from_central_function(
    lambda_session: Session, jwt_token_details: dict
) -> str:
    """Function that will invoke sync another Function in charge of getting the new token from a central function"""
    cdk_api_secret_arn = os.environ.get("CDK_API_SECRET_ARN_ROLE")
    client = set_calls_clients(cdk_api_secret_arn, lambda_session).client("lambda")
    try:
        new_token_r = client.invoke(
            FunctionName=CENTRAL_FUNCTION_ARN_TO_INVOKE,
            Payload=json.dumps(
                {
                    "vcluster": jwt_token_details["vcluster"],
                    "username": jwt_token_details["username"],
                    "expiry": NEW_TOKEN_LIFETIME_IN_SECONDS,
                }
            ),
        )
        res = json.loads(new_token_r["Payload"].read())
    except Exception as error:
        print(error)
        raise
    return res["token"]


def set_calls_clients(cdk_api_secret_arn: str, lambda_session: Session) -> Session:
    cdk_api_secret_role_arn = os.environ.get("CDK_API_SECRET_ARN_ROLE", None)
    if cdk_api_secret_role_arn and cdk_api_secret_arn.startswith("arn:aws"):
        return get_assume_role_session(lambda_session, cdk_api_secret_role_arn)
    return lambda_session


def get_cdk_gw_admin_creds(lambda_session: Session) -> dict:
    cdk_api_secret_arn = os.environ.get("CDK_API_SECRET_ARN")
    if not cdk_api_secret_arn:
        raise OSError("CDK_API_SECRET_ARN must be set.")
    client = set_calls_clients(cdk_api_secret_arn, lambda_session).client(
        "secretsmanager"
    )
    try:
        secret_value = client.get_secret_value(SecretId=cdk_api_secret_arn)[
            "SecretString"
        ]
    except Exception as error:
        logger.exception(error)
        logger.error(f"Failed to retrieve the SecretString for {cdk_api_secret_arn}")
        raise

    try:
        gw_secret = yaml.safe_load(secret_value)
    except yaml.YAMLError as error:
        logger.exception(error)
        logger.info("Secret string is not YAML formatted")
        try:
            gw_secret = json.loads(secret_value)
        except json.JSONDecodeError as error:
            logger.exception(error)
            logger.info("Secret string is not JSON formatted.")
            gw_secret = secret_value

    if not isinstance(gw_secret, (list, dict)):
        raise TypeError(
            "The secret format is not valid. Got {}, expected one of {}".format(
                str, (list, dict)
            )
        )
    for secret in gw_secret:
        if keyisset("admin", secret):
            return secret
    raise ValueError(f"No admin user found in {cdk_api_secret_arn}")


def get_vcluster_details_from_token(jwt_token: str) -> dict:
    """Uses existing secret JWT token to identify vcluster owner"""
    try:
        jwt_content = jwt.decode(
            jwt_token,
            options={"verify_signature": False},
            algorithms=["HS256", "HS384", "HS512"],
        )
        return jwt_content
    except Exception as error:
        logger.error(f"Jwt token decode error + {error}")
        raise error


def get_new_token_for_vcluster(
    gw_admin_secret: dict, vcluster: dict, life, token_only: bool = True
) -> str:
    try:
        logger.info(
            f"creating secret for {vcluster['vcluster']}/{vcluster['username']} with user on host {CDK_API_ENDPOINT}"
        )
        api_client = ApiClient(
            username=gw_admin_secret["username"],
            password=gw_admin_secret["password"],
            url=CDK_API_ENDPOINT,
        )
        proxy_client = ProxyClient(api_client)
        admin_client = VirturalClusters(proxy_client)
        logger.debug(admin_client.list_vclusters(as_list=True))
        token = admin_client.create_vcluster_user_token(
            vcluster=vcluster["vcluster"],
            username=vcluster["username"],
            lifetime_in_seconds=life,
            token_only=token_only,
        )
        return token
    except Exception as error:
        logger.exception(error)
        logger.error(
            "get_new_token_for_vcluster : Failed to create new jwt token for {}".format(
                vcluster["vcluster"]
            )
        )


def replace_string_in_dict_values(
    input_dict: dict, src_value: str, new_value: str, copy: bool = False
) -> dict:
    """
    Function to update all values in an input dictionary that will match with the new value.
    It uses the new value to set as regex and replaces it in the dict values for each key,
    allowing for any secret value and dynamic dict content.
    """

    src_re = re.compile(re.escape(src_value))
    if copy:
        updated_dict = deepcopy(input_dict)
    else:
        updated_dict = input_dict
    for key, value in updated_dict.items():
        if isinstance(value, str) and src_re.findall(value):
            updated_dict[key] = src_re.sub(new_value, value)
        elif not isinstance(value, str):
            print(f"The value for {key} is not a string. Skipping")
    if copy:
        return updated_dict
