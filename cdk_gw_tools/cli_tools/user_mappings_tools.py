#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

"""Functions to help with the user-mappings management"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdk_proxy_api_client.user_mappings import UserMappings
    from cdk_proxy_api_client.vclusters import VirtualClusters

from dacite import from_dict

from cdk_gw_tools.specs.user_mappings import DetailedIdentity, UserMappingsConfig


def create_export_config(
    vclusters: VirtualClusters, user_mappings: UserMappings
) -> UserMappingsConfig:
    """Lists all vClusters and returns the user mappings."""
    user_mappings_config: dict = {}
    mappings_config: dict = {"userMappings": user_mappings_config}
    _vclusters_list = vclusters.list_vclusters(as_list=True)
    for _vcluster_name in _vclusters_list["vclusters"]:
        _vcluster_mappings: list[dict] = []
        _vcluster_usernames: list[str] = user_mappings.list_mappings(
            vcluster_name=_vcluster_name
        ).json()
        for _username in _vcluster_usernames:
            _identity = user_mappings.get_user_mapping(
                username=_username, vcluster_name=_vcluster_name
            ).json()
            _vcluster_mappings.append(_identity)
        user_mappings_config[_vcluster_name] = {"identities": _vcluster_mappings}
    passthrough_users = user_mappings.list_mappings().json()
    passthrough_identities: list[dict] = []
    for _username in passthrough_users:
        passthrough_identities.append(
            user_mappings.get_user_mapping(username=_username).json()
        )
    user_mappings_config["passthrough"] = {"identities": passthrough_identities}
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


def handle_detailed_identity_input(
    user_mappings: UserMappings,
    existing_identities: list[tuple[str, str]],
    identity: DetailedIdentity,
    vcluster_name: str = None,
):
    """
    Checks if the username,principal combo already does exist. If it does,
    simply update (PUT) to update the mapping definition.
    If the combo doesn't exist, we evaluate against the existing pairs.
    Otherwise, we evaluate against each existing username,principal pair.
    If the username matches, but the principal doesn't, we update the principal, as this is an editable field
    If the username doesn't match, but the principal does, we delete the mapping altogether, and create it again, with
    the new username.
    If however none of these conditions are true, this is a new user-mapping and we create it.
    """
    to_create: tuple[str, str] = (
        identity.username,
        identity.principal,
    )
    if to_create in existing_identities:
        user_mappings.update_mapping(
            username=identity.username,
            principal=identity.principal,
            groups=identity.groups,
            vcluster_name=vcluster_name,
        )
        return
    for _existing_username, _existing_principal in existing_identities:
        if (
            identity.username == _existing_username
            and identity.principal != _existing_principal
        ):
            user_mappings.update_mapping(
                username=identity.username,
                principal=identity.principal,
                groups=identity.groups,
                vcluster_name=vcluster_name,
            )
            break
        elif (
            identity.username != _existing_username
            and identity.principal == _existing_principal
        ):
            user_mappings.delete_mapping(_existing_username, vcluster_name)
            user_mappings.create_mapping(
                username=identity.username,
                principal=identity.principal,
                groups=identity.groups,
                vcluster_name=vcluster_name,
            )
            break
    else:
        user_mappings.create_mapping(
            username=identity.username,
            principal=identity.principal,
            groups=identity.groups,
            vcluster_name=vcluster_name,
        )


def check_create_username_identity(
    user_mappings: UserMappings,
    identities_to_create: list[DetailedIdentity | str],
    existing_mappings: list[dict],
    vcluster_name: str | None = None,
) -> None:
    """
    Function to check and create the user mapping.
    Now (3.x+) that the user-mapping details has more than just the username, and previously the `username` was the
    `principal`, we check against the existence of both, just in case.
    """
    existing_identities: list[tuple[str, str]] = [
        (_mapping.get("username"), _mapping.get("principal"))
        for _mapping in existing_mappings
    ]
    for identity in identities_to_create:
        if isinstance(identity, str):
            warnings.warn(
                "For retro-compatibility, `strings` in the list of identities "
                "is maintained. It will be removed in a future version."
            )
            to_create = (
                identity,
                identity,
            )
            if to_create in existing_identities:
                user_mappings.update_mapping(
                    username=identity, principal=identity, vcluster_name=vcluster_name
                )
            else:
                user_mappings.create_mapping(
                    username=identity, principal=identity, vcluster_name=vcluster_name
                )
        elif isinstance(identity, DetailedIdentity):
            handle_detailed_identity_input(
                user_mappings,
                existing_identities,
                identity,
                vcluster_name=vcluster_name,
            )
        else:
            raise TypeError(
                f"Identity {identity} is not a string or a dict.", type(identity)
            )


def cleanup_undefined_identities(
    user_mappings: UserMappings,
    usernames_to_create: list[str],
    vcluster_name: str | None = None,
):
    """
    If a username is in existing identities but not in the list coming from the config file, delete
    the mapping.
    This helps with ensuring we use the config file as the target.
    """
    existing_usernames: list[str] = user_mappings.list_mappings(vcluster_name).json()
    for username in existing_usernames:
        if username not in usernames_to_create:
            user_mappings.delete_mapping(username=username, vcluster_name=vcluster_name)


def import_mappings_from_file(
    user_mappings: UserMappings, config: dict, remove_unset: bool = False
) -> None:
    """From the config file, will iterate over each vcluster to create/update/delete user-mappings."""
    mappings_config = validate_identities_are_unique(config)

    for _vcluster_name, definition in mappings_config.userMappings.items():
        vcluster_name: str | None = (
            None if _vcluster_name == "passthrough" else _vcluster_name
        )
        _existing_mappings = user_mappings.list_mappings_detailed(vcluster_name)
        usernames_to_create: list[str] = [
            _id.username
            for _id in definition.identities
            if isinstance(_id, DetailedIdentity)
        ] + [_id for _id in definition.identities if isinstance(_id, str)]
        check_create_username_identity(
            user_mappings,
            definition.identities,
            _existing_mappings,
            vcluster_name=vcluster_name,
        )
        if remove_unset:
            cleanup_undefined_identities(
                user_mappings, usernames_to_create, vcluster_name
            )
