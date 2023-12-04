#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Functions to help with the user-mappings management"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdk_proxy_api_client.usermappings import UserMappings
    from cdk_proxy_api_client.vclusters import VirturalClusters

from dataclasses import asdict

from cdk_gw_tools.specs.user_mappings import UserMappingsConfig


def create_export_config(
    vclusters: VirturalClusters, user_mappings: UserMappings
) -> UserMappingsConfig:
    """Lists all vClusters and returns the"""
    user_mappings_config: dict = {}
    mappings_config: dict = {"userMappings": user_mappings_config}
    _vclusters_list = vclusters.list_vclusters(as_list=True)
    for _vcluster_name in _vclusters_list["vclusters"]:
        _vcluster_mappings = user_mappings.list_mappings(vcluster=_vcluster_name).json()
        if _vcluster_mappings:
            user_mappings_config[_vcluster_name] = _vcluster_mappings
    return UserMappingsConfig(**mappings_config)


def import_mappings_from_file(
    vclusters, user_mappings, config: dict, remove_unset: bool = False
) -> dict:
    mappings_config = UserMappingsConfig(**config)
    _vclusters_list = vclusters.list_vclusters(as_list=True)["vclusters"]

    for vcluster_name, definition in mappings_config.userMappings.items():
        _existing_mappings = user_mappings.list_mappings(vcluster_name).json()
        for identity in definition:
            if identity not in _existing_mappings:
                user_mappings.create_mapping(vcluster_name, identity)
        if remove_unset:
            for identity in _existing_mappings:
                if identity not in definition:
                    print(
                        f"{vcluster_name} - {identity}:"
                        " identity is not defined in configuration, but present in existing mappings. Deleting."
                    )
                    user_mappings.delete_mapping(vcluster_name, identity)
    return asdict(create_export_config(vclusters, user_mappings))
