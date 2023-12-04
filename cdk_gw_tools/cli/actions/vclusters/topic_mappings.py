from __future__ import annotations

from os import path
from typing import Union

from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.vclusters import VirturalClusters
from compose_x_common.compose_x_common import keyisset, set_else_none

from cdk_gw_tools.cli_tools import load_config_file
from cdk_gw_tools.cli_tools.import_tenants_mappings import import_tenants_mappings


def format_vcluster_mappings_list(
    vcluster_name: str, req: list, options: dict
) -> Union[dict, list]:
    """Parses options to manipulate the returned list/dict"""
    mappings_list: list = []
    for _mapping in req:
        if keyisset("no_concentrated", options):
            if not keyisset("concentrated", _mapping):
                mappings_list.append(_mapping)
        elif keyisset("mapped_only", options):
            if not (
                keyisset("concentrated", _mapping)
                or _mapping["physicalTopicName"].startswith(vcluster_name)
            ):
                mappings_list.append(_mapping)
        else:
            mappings_list.append(_mapping)
    if keyisset("as_import_config", options):
        return {"tenant": vcluster_name, "mappings": mappings_list}
    return mappings_list


def tenant_mappings_actions(
    proxy: ProxyClient, vcluster: VirturalClusters, action: str, **kwargs
):
    """Manages actions for mappings vClusters actions"""

    vcluster_name = set_else_none("vcluster_name", kwargs)
    if action == "list":
        req = format_vcluster_mappings_list(
            vcluster_name,
            vcluster.list_vcluster_topic_mappings(vcluster_name).json(),
            kwargs,
        )
    elif action == "import-from-vclusters-config":
        content = load_config_file(path.abspath(kwargs["import_config_file"]))
        req = import_tenants_mappings(proxy, content, vcluster_name)
    elif action == "create":
        req = vcluster.create_vcluster_topic_mapping(
            vcluster=vcluster_name,
            logical_topic_name=kwargs["logical_topic_name"],
            physical_topic_name=kwargs["physical_topic_name"],
            read_only=keyisset("ReadOnly", kwargs),
            concentrated=keyisset("concentrated", kwargs),
            cluster_id=kwargs.get("cluster_id"),
        )
    elif action == "import-from-tenant":
        source_tenant = kwargs.pop("source_tenant")
        content = {
            "vcluster_name": vcluster_name,
            "mappings": [],
            "ignore_duplicates_conflict": True,
            "import_from_tenant": {"include_regex": [rf"^{source_tenant}$"]},
        }
        req = import_tenants_mappings(proxy, content, vcluster_name)
    elif action == "delete-topic-mapping":
        to_delete = kwargs.pop("logicalTopicName")
        req = vcluster.delete_vcluster_topic_mapping(
            vcluster=vcluster_name, logical_topic_name=to_delete
        )
    elif action == "delete-all-mappings":
        req = vcluster.delete_vcluster_topics_mappings(vcluster_name)
    else:
        raise NotImplementedError(f"Action {action} not yet implemented.")
    return req
