#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Handles retrieving the configuration file, defining clients, and returning them to subsequent CLI calls"""

from __future__ import annotations

import json

import yaml

try:
    from yaml import Loader as Loader
except ImportError:
    from yaml import CLoader as Loader

from json import loads

from boto3.session import Session
from cdk_proxy_api_client.proxy_api import ApiClient
from compose_x_common.compose_x_common import keyisset, set_else_none
from importlib_resources import files as pkg_files
from jsonschema import validate

from cdk_gw_tools.cli_tools import load_config_file

DEFAULT_SCHEMA_PATH = pkg_files("cdk_gw_tools").joinpath(
    "specs/profiles_config.spec.json"
)


def import_clients(
    config_file: str, client: str = None, schema: dict = None
) -> dict[str, ApiClient]:
    """
    Function that will validate input from specification, then create Proxy client based on the configuration defined.
    It returns a mapping with the profile name and the associated client.
    If client is set, only cares about that one client
    """
    content = load_config_file(config_file)
    if not schema:
        schema = loads(DEFAULT_SCHEMA_PATH.read_text())
    validate(content, schema)
    if client and client not in content:
        raise KeyError(f"Profile {client} not found in definition")

    client_profiles: dict = {}
    for profile, profile_config in content.items():
        if client and profile != client:
            continue
        url = set_else_none("Url", profile_config)
        if not url:
            raise KeyError(f"Url not defined for profile {profile}")
        username = set_else_none("Username", profile_config)
        password = set_else_none("Password", profile_config)
        aws_secrets_manager = set_else_none("AWSSecretsManager", profile_config)
        if username and password:
            client_profiles[profile] = ApiClient(
                url=url, username=username, password=password
            )
        elif aws_secrets_manager:
            client_profiles[profile] = set_profile_from_aws_secret(
                profile, url, aws_secrets_manager
            )
    return client_profiles


def set_profile_from_aws_secret(profile: str, url: str, aws_config: dict) -> ApiClient:
    """
    Uses the AWSSecretsManager configuration
    """
    session = Session(profile_name=set_else_none("ProfileName", aws_config, "default"))
    client = session.client("secretsmanager")
    user = set_else_none("Username", aws_config)
    try:
        secret_r = client.get_secret_value(SecretId=aws_config["SecretId"])
    except Exception as error:
        print(error)
        raise
    secret_format = set_else_none("Format", aws_config, "yaml")
    if secret_format == "yaml":
        secret_content = yaml.load(secret_r["SecretString"], Loader=Loader)
    else:
        secret_content = json.loads(secret_r["SecretString"])

    if not isinstance(secret_content, list):
        raise TypeError("The content of the secret must be a list of dict")

    for user_defined in secret_content:
        if user and user_defined["username"] == user:
            if not keyisset("admin", user_defined):
                print("The user {} is not admin. Some API calls might fail")
            return ApiClient(url=url, username=user, password=user_defined["password"])

        elif not user:
            if keyisset("admin", user_defined):
                # print(
                #     "Using {} for profile {}".format(user_defined["username"], profile)
                # )
                return ApiClient(
                    url=url,
                    username=user_defined["username"],
                    password=user_defined["password"],
                )

    raise LookupError(f"Unable to find an admin user to make API calls to {url}")
