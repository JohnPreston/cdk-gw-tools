#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

import json
import logging

from boto3.session import Session
from compose_x_common.compose_x_common import keyisset

from cdk_gw_tools.aws.gw_handling import (
    get_cdk_gw_admin_creds,
    get_new_token_for_vcluster,
    new_gateway_vcluster_secret_value,
)

if logging.getLogger().hasHandlers():
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()


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
                logger.error("The secret content is not a valid JSON.")
                raise
        if not isinstance(current_value, dict):
            raise TypeError(
                "The current value of the secret must be a dict. Got {}".format(
                    type(current_value)
                )
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


def create_secret(lambda_session: Session, arn, token, current_value: dict):
    """
    Creates the new secret for vcluster and stores in Secret with AWSPENDING stage.
    First, we check that there are no AWSPENDING secret value already in place.
    """
    client = lambda_session.client("secretsmanager")
    try:
        client.get_secret_value(
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
            new_secret_value: dict = new_gateway_vcluster_secret_value(
                current_value, lambda_session
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
