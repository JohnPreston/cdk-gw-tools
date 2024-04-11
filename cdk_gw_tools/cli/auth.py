# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations


def set_auth_actions(auth_subparsers):
    tenant_token_create_parser = auth_subparsers.add_parser(
        name="create", help="Create a new tenant token"
    )
    tenant_token_create_parser.add_argument(
        "--lifetime-in-seconds",
        dest="token_lifetime_in_seconds",
        type=int,
        help="Token lifetime in seconds. Sets expiry. Defaults 1 day (86400)",
        default=86400,
    )
    tenant_token_create_parser.add_argument(
        "--vcluster-name",
        help="Specify the vCluster this user token is for",
        required=False,
    )
    tenant_token_create_parser.add_argument(
        "--username",
        type=str,
        help="Sets the username to use for sasl.username to connect to the virtual cluster",
        required=False,
    )
    tenant_token_create_parser.add_argument(
        "--as-kafka-config",
        action="store_true",
        help="Returns the kafka config file",
        default=False,
    )
