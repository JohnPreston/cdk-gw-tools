#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Wrapper to configure mappings for a given tenant"""

from __future__ import annotations

import re
from copy import deepcopy
from json import loads

from cdk_proxy_api_client.common.logging import LOG
from cdk_proxy_api_client.errors import ProxyApiException, ProxyGenericException
from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.vclusters import VirturalClusters
from compose_x_common.compose_x_common import keyisset, set_else_none
from importlib_resources import files as pkg_files
from jsonschema import validate

DEFAULT_SCHEMA_PATH = pkg_files("cdk_gw_tools").joinpath(
    "specs/tenant_mappings-input.json"
)


def get_tenant_logical_topics(
    proxy: ProxyClient, tenant_name: str, include_read_only: bool = False
) -> list[dict]:
    """
    Returns the list of topics (logical name) from a given tenant topics mappings. Ignores
    :param ProxyClient proxy:
    :param str tenant_name:
    :param bool include_read_only:
    :return: List of topics logical available in the tenant.
    """
    tenant_mappings = VirturalClusters(proxy)

    topics_list: list[dict] = []
    for _topic in tenant_mappings.list_vcluster_topic_mappings(
        tenant_name, as_list=True
    ):
        if _topic["readOnly"] is True and not include_read_only:
            continue
        topics_list.append(_topic)
    return topics_list


def import_from_tenants_include_string(
    proxy: ProxyClient,
    include_regex: str,
    vcluster_name: str,
    tenants: list[str],
    processed_tenants: list[str],
    process_once: bool = False,
) -> None:
    """Matches tenant based on simple string regex"""
    try:
        _pattern = re.compile(include_regex)
    except Exception as error:
        print(error)
        print(include_regex, "Not a valid regex")
        return
    tenant_mappings = VirturalClusters(proxy)
    for _tenant in tenants:
        if _pattern.match(_tenant):
            if process_once and _tenant in processed_tenants:
                print(
                    f"Tenant {_tenant} was already processed. Skipping",
                    processed_tenants,
                )
                continue
            else:
                tenant_topics: list[dict] = get_tenant_logical_topics(proxy, _tenant)
                for _import_tenant_topic in tenant_topics:
                    tenant_mappings.create_vcluster_topic_mapping(
                        vcluster_name,
                        _import_tenant_topic["logicalTopicName"],
                        _import_tenant_topic["physicalTopicName"],
                        read_only=False,
                    )
                processed_tenants.append(_tenant)


def import_from_tenants_include_dict(
    proxy: ProxyClient,
    mapping_import_config: dict,
    tenant_name: str,
    tenants: list[str],
    processed_tenants: list[str],
    process_once: bool = False,
) -> None:
    """Import topic mappings tenants from complex definition"""
    try:
        _pattern = re.compile(mapping_import_config["tenant_regex"])
    except Exception as error:
        print(error)
        print(mapping_import_config["tenant_regex"], "Not a valid regex")
        return
    topics_exclude_pattern_regexes: list = set_else_none(
        "logical_topics_exclude_regexes", mapping_import_config
    )
    topics_include_pattern_regexes: list = set_else_none(
        "logical_topics_include_regexes", mapping_import_config, ["^(.*)$"]
    )
    topics_exclude_patterns: list[re.Pattern] = []
    topics_include_patterns: list[re.Pattern] = []
    if topics_exclude_pattern_regexes:
        for _exclude_pattern in topics_exclude_pattern_regexes:
            try:
                topics_exclude_patterns.append(re.compile(_exclude_pattern))
            except Exception as error:
                LOG.exception(error)
                LOG.error(
                    "logical_topics_exclude_regexes",
                    _exclude_pattern,
                    "Not a valid regex. Skipping",
                )
                return
    if topics_include_pattern_regexes:
        for _include_pattern in topics_include_pattern_regexes:
            try:
                topics_include_patterns.append(re.compile(_include_pattern))
            except Exception as error:
                LOG.exception(error)
                LOG.error(
                    "logical_topics_include_regexes",
                    _include_pattern,
                    "Not a valid regex. Skipping",
                )
                return

    tenant_mappings = VirturalClusters(proxy)
    for _tenant in tenants:
        if _pattern.match(_tenant):
            if process_once and _tenant in processed_tenants:
                LOG.debug(
                    "Tenant {} was already processed. Skipping {}".format(
                        _tenant, processed_tenants
                    ),
                )
                continue
            else:
                processed_tenants.append(_tenant)
        else:
            LOG.debug(f"Skipping tenant {_tenant}")
            continue
        tenant_topics: list[dict] = get_tenant_logical_topics(proxy, _tenant)
        topics_to_import: list[dict] = deepcopy(tenant_topics)
        for _import_tenant_topic in tenant_topics:
            for _exclude_pattern in topics_exclude_patterns:
                if (
                    _exclude_pattern.match(_import_tenant_topic["logicalTopicName"])
                    and _import_tenant_topic["logicalTopicName"] in topics_to_import
                ):
                    topics_to_import.remove(_import_tenant_topic)
                    LOG.debug(
                        "Topic: {} matched against exclude regex: {}".format(
                            _import_tenant_topic["logicalTopicName"],
                            _exclude_pattern.pattern,
                        ),
                    )
        LOG.debug(
            "Topics post exclude", [_t["logicalTopicName"] for _t in topics_to_import]
        )
        final_topics_import: list[dict] = []
        for _import_tenant_topic in topics_to_import:
            for _include_pattern in topics_include_patterns:
                if (
                    _include_pattern.match(_import_tenant_topic["logicalTopicName"])
                    and _import_tenant_topic not in final_topics_import
                ):
                    final_topics_import.append(_import_tenant_topic)
                    break
        LOG.debug(f"Tenant:{_tenant} - Final topic list:{final_topics_import}")
        grant_write_access = keyisset("grant_write_access", mapping_import_config)
        for topic_mapping in final_topics_import:
            try:
                tenant_mappings.create_vcluster_topic_mapping(
                    tenant_name,
                    topic_mapping["logicalTopicName"],
                    topic_mapping["physicalTopicName"],
                    read_only=not grant_write_access,
                )
                if grant_write_access:
                    LOG.warn(
                        "{}:{} - Granting write access.".format(
                            _tenant, topic_mapping["physicalTopicName"]
                        )
                    )
            except ProxyApiException:
                print(
                    "Failed to create mapping from {}: {} does not seem to exist.".format(
                        _tenant, topic_mapping["physicalTopicName"]
                    )
                )


def import_from_other_tenants(
    proxy: ProxyClient, import_config: dict, tenant_name: str
) -> None:
    """Allows to import existing topics from other tenants in read-only"""
    tenants: list[str] = VirturalClusters(proxy).list_vclusters(as_list=True)
    exclude_list = set_else_none("exclude_regex", import_config, [])
    include_list = set_else_none("include_regex", import_config, [])
    processed_tenants: list[str] = []
    process_once: bool = keyisset("process_tenant_only_once", import_config)
    if not include_list:
        raise ValueError("There must be at least one item in include_regex")
    for _regex in exclude_list:
        try:
            _pattern = re.compile(_regex)
            for _tenant in tenants:
                if _pattern.match(_tenant):
                    tenants.remove(_tenant)
        except Exception as error:
            print(error)
            print(_regex, "not a valid regex. Ignoring")
    for _include_item in include_list:
        if isinstance(_include_item, str):
            import_from_tenants_include_string(
                proxy,
                _include_item,
                tenant_name,
                tenants,
                processed_tenants,
                process_once,
            )
        elif isinstance(_include_item, dict):
            import_from_tenants_include_dict(
                proxy,
                _include_item,
                tenant_name,
                tenants,
                processed_tenants,
                process_once,
            )
        else:
            raise TypeError(
                _include_item,
                "is of type",
                type(_include_item),
                "expected one of",
                (str, dict),
            )


def propagate_tenant_mappings(
    tenant_mappings: VirturalClusters,
    mappings: list[dict],
    tenant_name: str,
    ignore_conflicts: bool = False,
) -> None:
    for mapping in mappings:
        print("MAPPINGS IMPORT", mapping)
        try:
            tenant_mappings.create_vcluster_topic_mapping(
                tenant_name,
                mapping["logicalTopicName"],
                mapping["physicalTopicName"],
                read_only=keyisset("readOnly", mapping),
                concentrated=keyisset("concentrated", mapping),
            )
        except ProxyGenericException as error:
            if error.code == 409 and ignore_conflicts:
                pass


def import_tenants_mappings(
    client: ProxyClient, config_content: dict, tenant_name: str, schema: dict = None
) -> list[dict]:
    """Will create mappings from the config content, and return the final mappings for the tenant"""
    if not schema:
        schema = loads(DEFAULT_SCHEMA_PATH.read_text())
    validate(config_content, schema)
    tenant_name = set_else_none("tenant_name", config_content, tenant_name)
    ignore_conflicts = keyisset("ignore_duplicates_conflict", config_content)
    mappings = config_content["mappings"]
    tenant_mappings = VirturalClusters(client)
    propagate_tenant_mappings(tenant_mappings, mappings, tenant_name, ignore_conflicts)
    import_from_other_tenants_config = set_else_none(
        "import_from_tenant", config_content
    )
    if import_from_other_tenants_config:
        import_from_other_tenants(client, import_from_other_tenants_config, tenant_name)

    return tenant_mappings.list_vcluster_topic_mappings(tenant_name, True)
