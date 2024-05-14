# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from dataclasses import asdict

from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.user_mappings import UserMappings
from cdk_proxy_api_client.vclusters import VirtualClusters
from compose_x_common.compose_x_common import keyisset

from cdk_gw_tools.cli_actions.common import format_return
from cdk_gw_tools.cli_tools import load_config_file
from cdk_gw_tools.cli_tools.user_mappings_tools import (
    create_export_config,
    import_mappings_from_file,
    validate_identities_are_unique,
)


@format_return
def user_mappings_actions(proxy: ProxyClient, action: str, **kwargs):
    """
    Handles user-mappings cli_actions
    """
    vclusters = VirtualClusters(proxy)
    user_mappings = UserMappings(proxy)
    if action == "list":
        if kwargs.get("detailed"):
            return user_mappings.list_mappings_detailed(
                vcluster_name=kwargs.get("vcluster_name", None)
            )
        return user_mappings.list_mappings(
            vcluster_name=kwargs.get("vcluster_name", None)
        )
    elif action == "describe":
        return user_mappings.get_user_mapping(
            username=kwargs.get("username"), vcluster_name=kwargs.get("vcluster_name")
        )
    elif action == "create":
        return user_mappings.create_mapping(
            kwargs.get("username"),
            principal=kwargs.get("principal"),
            groups=kwargs.get("groups"),
            vcluster_name=kwargs.get("vcluster_name"),
        )
    elif action == "delete":
        return user_mappings.delete_mapping(
            username=kwargs.get("username"),
            vcluster_name=kwargs.get("vcluster_name", None),
        )
    elif action == "export":
        req = create_export_config(vclusters, user_mappings)
        return asdict(req)
    elif action == "import":
        config = load_config_file(kwargs["import_file"])
        import_mappings_from_file(
            user_mappings, config, keyisset("remove_unset", kwargs)
        )
        return {"status": "imported"}
    elif action == "validate":
        config = load_config_file(kwargs["import_file"])
        validate_identities_are_unique(config)
        return {"status": "valid"}
    else:
        raise NotImplementedError(f"Action {action} is not implemented yet.")
