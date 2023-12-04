from __future__ import annotations

from cdk_proxy_api_client.proxy_api import ProxyClient
from cdk_proxy_api_client.usermappings import UserMappings


def user_mappings_actions(proxy: ProxyClient, action: str, **kwargs):
    """
    Handles vCluster OAuth mappings actions
    """
    user_mappings = UserMappings(proxy)
    if action == "list":
        return user_mappings.list_mappings(kwargs["vcluster_name"])
    elif action == "create":
        return user_mappings.create_mapping(kwargs["vcluster_name"], kwargs["username"])
    elif action == "delete":
        return user_mappings.delete_mapping(kwargs["vcluster_name"], kwargs["username"])
    else:
        raise NotImplementedError(
            f"Action {action} not yet implemented for user mappings."
        )
