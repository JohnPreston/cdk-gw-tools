# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from argparse import ArgumentParser

VCLUSTER_PARSER = ArgumentParser(add_help=False)
VCLUSTER_PARSER.add_argument(
    "--vcluster-name",
    dest="vcluster_name",
    required=True,
    help="Name of the vcluster to make operations for",
)


def set_user_mappings_actions_parsers(user_mappings_subparsers):
    user_mappings_parser = user_mappings_subparsers.add_parser(
        name="user-mappings",
        help="Manages vCluster user mappings",
        parents=[VCLUSTER_PARSER],
    )
    user_mappings_sub_parsers = user_mappings_parser.add_subparsers(dest="sub_action")

    list_parser = user_mappings_sub_parsers.add_parser(
        name="list", help="List all user mappings for vCluster"
    )

    create_parser = user_mappings_sub_parsers.add_parser(
        name="create", help="Create user mapping for vCluster"
    )
    create_parser.add_argument(
        "--username",
        required=True,
        help="Value of the `sub` of the JWT token from your issuer",
    )

    delete_parser = user_mappings_sub_parsers.add_parser(
        name="delete", help="Create user mapping for vCluster"
    )
    delete_parser.add_argument(
        "--username",
        required=True,
        help="Value of the `sub` of the JWT token from your issuer",
    )
