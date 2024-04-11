# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdk_proxy_api_client.proxy_api import ProxyClient

from cdk_proxy_api_client.vclusters import VirtualClusters
from compose_x_common.compose_x_common import keyisset


def auth_actions(proxy_client: ProxyClient, action: str, **kwargs):
    """Manages cli_actions for auth vClusters subparser"""
    username = kwargs.get("username") or kwargs["vcluster_name"]
    if action == "create":
        vcluster_client = VirtualClusters(proxy_client)
        req = vcluster_client.create_vcluster_user_token(
            vcluster=kwargs.get("vcluster_name"),
            username=username,
            lifetime_in_seconds=int(kwargs.get("token_lifetime_in_seconds")),
            token_only=keyisset("token_only", kwargs),
        )
    else:
        raise NotImplementedError(f"Action {action} not yet implemented.")
    if keyisset("as_kafka_config", kwargs):
        req = req.json()
        return """security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="{}" password="{}";
client.id=CLI_{}""".format(
            username, req["token"], username
        )
    return req
