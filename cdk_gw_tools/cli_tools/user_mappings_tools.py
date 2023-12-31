#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Functions to help with the user-mappings management"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdk_proxy_api_client.usermappings import UserMappings
    from cdk_proxy_api_client.vclusters import VirturalClusters

from dacite import from_dict

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
            user_mappings_config[_vcluster_name] = {"identities": _vcluster_mappings}
    return from_dict(UserMappingsConfig, mappings_config)


def validate_identities_are_unique(config: dict) -> UserMappingsConfig:
    mappings_config = from_dict(UserMappingsConfig, config)
    identities_recorded: list = []
    for definition in mappings_config.userMappings.values():
        for identity in definition.identities:
            if identity in identities_recorded:
                raise ValueError(f"Identity {identity} is defined multiple times.")
            identities_recorded.append(identity)
    return mappings_config


def import_mappings_from_file(
    vclusters, user_mappings, config: dict, remove_unset: bool = False
) -> UserMappingsConfig:
    mappings_config = validate_identities_are_unique(config)

    for vcluster_name, definition in mappings_config.userMappings.items():
        _existing_mappings = user_mappings.list_mappings(vcluster_name).json()
        for identity in definition.identities:
            if identity not in _existing_mappings:
                user_mappings.create_mapping(vcluster_name, identity)
        if remove_unset:
            for identity in _existing_mappings:
                if identity not in definition.identities:
                    print(
                        f"{vcluster_name} - {identity}:"
                        " identity is not defined in configuration, but present in existing mappings. Deleting."
                    )
                    user_mappings.delete_mapping(vcluster_name, identity)
    return create_export_config(vclusters, user_mappings)
