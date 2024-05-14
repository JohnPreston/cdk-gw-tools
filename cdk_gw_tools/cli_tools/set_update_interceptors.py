#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Wrapper to configure mappings for a given tenant"""

from __future__ import annotations

import json
from dataclasses import asdict

from cdk_proxy_api_client.interceptors import Interceptors
from cdk_proxy_api_client.plugins import Plugins
from cdk_proxy_api_client.proxy_api import ProxyClient
from dacite import from_dict

from cdk_gw_tools.specs.interceptors_config import *


def set_update_for_interceptor_context(
    interceptors_client: Interceptors,
    plugin_class: str,
    interceptor_context: InterceptorContext,
    interceptor_name: str,
    vcluster_name: str = None,
):
    """Sets the interceptor for a given Interceptor Context"""
    if interceptor_context.definition:
        plugin_config: dict = asdict(interceptor_context.definition)
        plugin_config["pluginClass"] = plugin_class
        interceptors_client.update_interceptor(
            interceptor_name=interceptor_name,
            interceptor_config=plugin_config,
            vcluster_name=vcluster_name,
        )
    if interceptor_context.groups:
        for group_name, group_config in interceptor_context.groups.items():
            plugin_config: dict = asdict(group_config)
            plugin_config["pluginClass"] = plugin_class
            interceptors_client.update_interceptor(
                interceptor_name,
                interceptor_config=plugin_config,
                group_name=group_name,
                vcluster_name=vcluster_name,
            )
    if interceptor_context.usernames:
        for user_name, user_config in interceptor_context.usernames.items():
            plugin_config: dict = asdict(user_config)
            plugin_config["pluginClass"] = plugin_class
            interceptors_client.update_interceptor(
                interceptor_name,
                interceptor_config=plugin_config,
                username=user_name,
                vcluster_name=vcluster_name,
            )


def set_update_interceptors(proxy: ProxyClient, interceptors: dict):
    plugins_client = Plugins(proxy)
    interceptors_client = Interceptors(proxy)
    plugins_list = plugins_client.list_all_plugins(as_list=True)
    gw_interceptors_config: GwInterceptorsConfig = from_dict(
        data_class=GwInterceptorsConfig, data=interceptors
    )
    for (
        interceptor_name,
        interceptor_config,
    ) in gw_interceptors_config.interceptors.items():
        plugin_class = interceptor_config.pluginClass
        if plugin_class not in plugins_list:
            raise ValueError(
                "Interceptor %s does not exist. Available ones"
                % (interceptor_config.pluginClass,),
                plugins_list,
            )
        if interceptor_config.gateway:
            plugin_config: dict = asdict(interceptor_config.gateway)
            plugin_config["pluginClass"] = plugin_class
            interceptors_client.update_interceptor(
                interceptor_name=interceptor_name,
                interceptor_config=plugin_config,
                is_global=True,
            )
        if interceptor_config.passthrough:
            set_update_for_interceptor_context(
                interceptors_client,
                plugin_class,
                interceptor_config.passthrough,
                interceptor_name,
            )
        if interceptor_config.vclusters:
            for vcluster_name, vcluster_context in interceptor_config.vclusters.items():
                set_update_for_interceptor_context(
                    interceptors_client,
                    plugin_class,
                    vcluster_context,
                    interceptor_name,
                    vcluster_name=vcluster_name,
                )
