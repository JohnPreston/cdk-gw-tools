# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

import json
import warnings

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from cdk_proxy_api_client.interceptors import Interceptors
from cdk_proxy_api_client.proxy_api import ProxyClient
from compose_x_common.compose_x_common import keyisset, set_else_none

from cdk_gw_tools.cli_tools import load_config_file


def interceptors_actions(proxy: ProxyClient, action: str, **kwargs):
    """Triggers function according to CLI Input"""

    _interceptor_client = Interceptors(proxy)
    if action == "list-all":
        return _interceptor_client.get_all_gw_interceptors().json()
    if action == "list":
        _interceptors = _interceptor_client.get_all_interceptor(
            is_global=kwargs.get("is_global"),
            username=kwargs.get("username"),
            group_name=kwargs.get("group_name"),
            vcluster_name=kwargs.get("vcluster_name"),
        ).json()
        if keyisset("IgnoreReadOnly", kwargs):
            return [
                _interceptor
                for _interceptor in _interceptors.values()
                if _interceptor["pluginClass"]
                != "io.conduktor.gateway.interceptor.safeguard.ReadOnlyTopicPolicyPlugin"
            ]
        return _interceptors
    elif action == "create-update":
        warnings.warn(
            "We highly recommend to use this command for testing only."
            "Use the import command to declare the interceptors you want to define as-code"
        )
        config = load_config_file(kwargs["config_file_path"])

        _req = _interceptor_client.update_interceptor(
            kwargs.get("interceptor_name"),
            config,
            is_global=kwargs.get("is_global"),
            vcluster_name=kwargs["vcluster_name"],
            username=kwargs.get("username"),
            group_name=kwargs.get("group_name"),
        ).json()
        return _req
    elif action == "delete":
        _req = _interceptor_client.delete_interceptor(
            interceptor_name=kwargs.get("interceptor_name"),
            is_global=kwargs.get("is_global"),
            vcluster_name=kwargs["vcluster_name"],
            username=kwargs.get("username"),
            group_name=kwargs.get("group_name"),
        ).status_code
        return _req
    elif action == "import-from-config":
        _loaded_config = load_config_file(kwargs["config_file_path"])
        if not keyisset("interceptors", _loaded_config):
            return
        from cdk_gw_tools.cli_tools.set_update_interceptors import (
            set_update_interceptors,
        )

        _req = set_update_interceptors(proxy, _loaded_config)
    return None
