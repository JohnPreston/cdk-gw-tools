#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Wrapper to configure mappings for a given tenant"""

from __future__ import annotations

from cdk_proxy_api_client.errors import GenericNotFound, ProxyGenericException
from cdk_proxy_api_client.interceptors import Interceptors
from cdk_proxy_api_client.plugins import Plugins
from cdk_proxy_api_client.proxy_api import ProxyClient
from compose_x_common.compose_x_common import keyisset


def set_update_interceptors(proxy: ProxyClient, vcluster_name: str, interceptors: dict):
    plugins_client = Plugins(proxy)
    interceptors_client = Interceptors(proxy)
    try:
        plugins_list = plugins_client.list_all_plugins(as_list=True)
    except GenericNotFound as error:
        _plugins_list = plugins_client.list_all_plugins(as_list=True, extended=True)
        plugins_list = [p["pluginId"] for p in _plugins_list]

    for interceptor_name, interceptor_def in interceptors.items():
        plugin_class: str = interceptor_def.pop("pluginClass")
        if plugin_class not in plugins_list:
            raise ValueError(
                "The selected pluginClass {} is not available. Must be one of {}".format(
                    plugin_class, plugins_list
                )
            )
        if keyisset("username", interceptor_def):
            username = interceptor_def.pop("username")
        else:
            username = None
        try:
            interceptors_client.create_vcluster_interceptor(
                vcluster_name=vcluster_name,
                interceptor_name=interceptor_name,
                plugin_class=plugin_class,
                priority=int(interceptor_def["priority"]),
                config=interceptor_def["config"],
                username=username,
            )
            print(
                "Successfully created interceptor {} for {}".format(
                    interceptor_name, vcluster_name
                )
            )
        except ProxyGenericException:
            interceptors_client.update_vcluster_interceptor(
                vcluster_name=vcluster_name,
                interceptor_name=interceptor_name,
                plugin_class=plugin_class,
                priority=int(interceptor_def["priority"]),
                config=interceptor_def["config"],
                username=username,
            )
            print(f"Successfully updated {interceptor_name} for {vcluster_name}")
        except Exception as error:
            print(error)
            raise
