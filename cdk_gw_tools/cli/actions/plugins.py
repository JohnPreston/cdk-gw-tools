# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from cdk_proxy_api_client.plugins import Plugins
from cdk_proxy_api_client.proxy_api import ProxyClient
from compose_x_common.compose_x_common import keyisset

from cdk_gw_tools.cli import format_return


@format_return
def plugins_actions(proxy: ProxyClient, action: str, **kwargs):
    _plugins = Plugins(proxy)
    if action == "list":
        req = _plugins.list_all_plugins(
            extended=keyisset("extended", kwargs), as_list=keyisset("as_list", kwargs)
        )
    else:
        raise NotImplementedError(f"Action {action} is not implemented yet.")
    return req
