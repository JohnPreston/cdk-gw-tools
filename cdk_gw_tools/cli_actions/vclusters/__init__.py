# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

"""Manages the vclusters <action> of the CLI"""

from __future__ import annotations

from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.vclusters import VirtualClusters

from cdk_gw_tools.cli_actions.auth import auth_actions
from cdk_gw_tools.cli_actions.common import format_return
from cdk_gw_tools.cli_actions.interceptors import interceptors_actions
from cdk_gw_tools.cli_actions.user_mappings import user_mappings_actions
from cdk_gw_tools.cli_actions.vclusters.topic_mappings import vcluster_mappings_actions


def concentration_rules_actions(vclusters: VirtualClusters, action: str, **kwargs):
    if action == "list":
        req = vclusters.get_concentration_rules(
            vcluster_name=kwargs.get("vcluster_name")
        )
    elif action == "create":
        req = vclusters.create_concentration_rule(
            kwargs.get("vcluster_name"),
            kwargs.get("pattern"),
            delete_topic_name=kwargs.get("deleteTopicName"),
            compact_topic_name=kwargs.get(
                "compactTopicName", f"{kwargs.get('deleteTopicName')}_compact"
            ),
            compact_delete_topic_name=kwargs.get(
                "deleteCompactTopicName",
                f"{kwargs.get('deleteTopicName')}_delete_compact",
            ),
            cluster_id=kwargs.get("cluster_id"),
        )
    elif action == "delete":
        req = vclusters.delete_concentration_rule(
            vcluster_name=kwargs.get("vcluster_name"),
            pattern=kwargs.get("pattern"),
        )
    else:
        raise NotImplementedError(f"Action {action} not yet implemented.")
    return req


@format_return
def vclusters_actions(proxy: ProxyClient, action: str, **kwargs):
    """Manages execution of vClusters"""
    vclusters = VirtualClusters(proxy)
    if action == "list":
        req = vclusters.list_vclusters(as_list=True)
    elif action == "mappings":
        req = vcluster_mappings_actions(
            proxy, vclusters, kwargs.pop("sub_action"), **kwargs
        )
    elif action == "concentration-rules":
        req = concentration_rules_actions(vclusters, kwargs.pop("sub_action"), **kwargs)
    elif action == "interceptors":
        req = interceptors_actions(proxy, kwargs.pop("sub_action"), **kwargs)
    elif action == "user-mappings":
        req = user_mappings_actions(proxy, kwargs.pop("sub_action"), **kwargs)
    else:
        raise NotImplementedError(f"Action {action} not yet implemented.")
    return req
