# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from dataclasses import asdict

from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.usermappings import UserMappings
from cdk_proxy_api_client.vclusters import VirturalClusters
from compose_x_common.compose_x_common import keyisset

from cdk_gw_tools.cli import format_return
from cdk_gw_tools.cli_tools import load_config_file
from cdk_gw_tools.cli_tools.user_mappings_tools import (
    create_export_config,
    import_mappings_from_file,
    validate_identities_are_unique,
)


@format_return
def gw_user_mappings_actions(proxy: ProxyClient, action: str, **kwargs) -> dict:
    vclusters = VirturalClusters(proxy)
    user_mappings = UserMappings(proxy)
    if action == "export":
        req = create_export_config(vclusters, user_mappings)
    elif action == "import":
        config = load_config_file(kwargs["import_file"])
        req = import_mappings_from_file(
            vclusters, user_mappings, config, keyisset("remove_unset", kwargs)
        )
    elif action == "validate":
        config = load_config_file(kwargs["import_file"])
        validate_identities_are_unique(config)
    else:
        raise NotImplementedError(f"Action {action} is not implemented yet.")
    return asdict(req)
