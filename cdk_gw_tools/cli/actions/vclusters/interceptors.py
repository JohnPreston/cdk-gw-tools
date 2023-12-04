# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

import json

from cdk_proxy_api_client.interceptors import Interceptors
from cdk_proxy_api_client.proxy_api import ProxyClient
from compose_x_common.compose_x_common import keyisset, set_else_none

from cdk_gw_tools.cli_tools import load_config_file


def interceptors_actions(proxy: ProxyClient, action: str, **kwargs):
    """Triggers function according to CLI Input"""

    _interceptor_client = Interceptors(proxy)
    if action == "list":
        _interceptors = _interceptor_client.list_vcluster_interceptors(
            vcluster_name=kwargs["vcluster_name"], as_list=True
        )
        if keyisset("IgnoreReadOnly", kwargs):
            return [
                _interceptor
                for _interceptor in _interceptors.values()
                if _interceptor["pluginClass"]
                != "io.conduktor.gateway.interceptor.safeguard.ReadOnlyTopicPolicyPlugin"
            ]
        return _interceptors
    elif action == "create-update":
        with open(kwargs["config"]) as config_fd:
            config_raw = config_fd.read()
            config_json = json.loads(config_raw)
        _req = _interceptor_client.create_vcluster_interceptor(
            vcluster_name=kwargs["vcluster_name"],
            interceptor_name=config_json["name"],
            plugin_class=config_json["pluginClass"],
            priority=config_json["priority"],
            config=config_json["config"],
            username=set_else_none("vcluster_username", kwargs, None),
        )
        return _req
    elif action == "delete":
        _req = _interceptor_client.delete_vcluster_interceptor(
            kwargs["vcluster_name"],
            kwargs["interceptor_name"],
            set_else_none("vcluster_username", kwargs, None),
        )
        return _req
    elif action == "import-from-config":
        _loaded_config = load_config_file(kwargs["InputConfigFile"])
        if not keyisset("interceptors", _loaded_config):
            return
        from cdk_gw_tools.cli_tools.set_update_interceptors import (
            set_update_interceptors,
        )

        _req = set_update_interceptors(
            proxy, kwargs["vcluster_name"], _loaded_config["interceptors"]
        )
    return None
