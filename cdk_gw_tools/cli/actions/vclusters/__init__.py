# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

"""Manages the vclusters <action> of the CLI"""

from __future__ import annotations

from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.vclusters import VirturalClusters

from cdk_gw_tools.cli import format_return
from cdk_gw_tools.cli.actions.vclusters.auth import auth_actions
from cdk_gw_tools.cli.actions.vclusters.interceptors import interceptors_actions
from cdk_gw_tools.cli.actions.vclusters.topic_mappings import tenant_mappings_actions
from cdk_gw_tools.cli.actions.vclusters.user_mappings import user_mappings_actions


@format_return
def vclusters_actions(proxy: ProxyClient, action: str, **kwargs):
    """Manages execution of vClusters"""
    vclusters = VirturalClusters(proxy)
    if action == "list":
        req = vclusters.list_vclusters(as_list=True)
    elif action == "auth":
        req = auth_actions(vclusters, kwargs.pop("sub_action"), **kwargs)
    elif action == "mappings":
        req = tenant_mappings_actions(
            proxy, vclusters, kwargs.pop("sub_action"), **kwargs
        )
    elif action == "interceptors":
        req = interceptors_actions(proxy, kwargs.pop("sub_action"), **kwargs)
    elif action == "user-mappings":
        req = user_mappings_actions(proxy, kwargs.pop("sub_action"), **kwargs)
    else:
        raise NotImplementedError(f"Action {action} not yet implemented.")
    return req
