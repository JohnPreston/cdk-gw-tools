#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

import json
import logging
import sys

import yaml

try:
    from yaml import Dumper
except ImportError:
    from yaml import CDumper as Dumper

from cdk_proxy_api_client.proxy_api import ApiClient, ProxyClient

from cdk_gw_tools.cli.actions import format_return
from cdk_gw_tools.cli.actions.plugins import plugins_actions
from cdk_gw_tools.cli.actions.user_mappings import gw_user_mappings_actions
from cdk_gw_tools.cli.actions.vclusters import vclusters_actions
from cdk_gw_tools.cli.actions.vclusters.interceptors import interceptors_actions
from cdk_gw_tools.cli.main_parser import set_parser
from cdk_gw_tools.cli_tools.import_from_config import import_clients
from cdk_gw_tools.common.logging import LOG


def main():
    _PARSER = set_parser()
    _args = _PARSER.parse_args()
    if hasattr(_args, "loglevel") and _args.loglevel:
        valid_levels = [
            "FATAL",
            "CRITICAL",
            "ERROR",
            "WARNING",
            "WARN",
            "INFO",
            "DEBUG",
            "INFO",
        ]
        if _args.loglevel.upper() in valid_levels:
            LOG.setLevel(logging.getLevelName(_args.loglevel.upper()))
            LOG.handlers[0].setLevel(logging.getLevelName(_args.loglevel.upper()))
        else:
            print(
                f"Log level value {_args.loglevel} is invalid. Must me one of {valid_levels}"
            )
    _vars = vars(_args)
    if _args.url:
        if not _args.username or not _args.password:
            raise Exception(
                "If you specify URL, you must specify username and password too"
            )
        _client = ApiClient(
            username=_vars.pop("username"),
            password=_vars.pop("password"),
            url=_vars.pop("url"),
        )
    elif _args.profile_name:
        _clients = import_clients(_args.config_file)
        _client = _clients[_args.profile_name]
    else:
        raise Exception(
            "You must either set --profile-name (possibly -c) or define --url, --username and --password"
        )
    _category = _vars.pop("category")
    _action = _vars.pop("action")
    _proxy = ProxyClient(_client)

    _categories_mappings: dict = {
        "vclusters": vclusters_actions,
        "plugins": plugins_actions,
        "user-mappings": gw_user_mappings_actions,
    }
    dest_function = _categories_mappings[_category]
    response = dest_function(_proxy, _action, **_vars)
    if not response:
        return
    if isinstance(response, str):
        print(response)
        return
    try:
        if _args.output_format == "json":
            print(json.dumps(response, indent=2))
        else:
            print(yaml.dump(response, Dumper=Dumper))
    except Exception as error:
        print(error)
        print(response)


if __name__ == "__main__":
    sys.exit(main())
