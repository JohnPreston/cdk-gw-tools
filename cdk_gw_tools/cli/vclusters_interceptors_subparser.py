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

USERNAME_PARSER = ArgumentParser(add_help=False)
USERNAME_PARSER.add_argument(
    "--username",
    dest="vcluster_username",
    required=False,
    help="Specify username to get interceptors for",
)


def set_interceptors_actions_parsers(vclusters_subparsers):
    """Creates all the parser and subparsers for vClusters API endpoints"""

    interceptors_parser = vclusters_subparsers.add_parser(
        name="interceptors",
        help="List vCluster interceptors",
        parents=[VCLUSTER_PARSER],
    )
    interceptors_subparsers = interceptors_parser.add_subparsers(dest="sub_action")
    list_parser = interceptors_subparsers.add_parser(
        name="list",
        help="List interceptors for vcluster/username",
        parents=[USERNAME_PARSER],
    )
    create_parser = interceptors_subparsers.add_parser(
        name="create-update",
        help="Create or update a new vCluster mapping",
        parents=[USERNAME_PARSER],
    )
    # create_parser.add_argument("--interceptor-name", type=str, required=True)
    create_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to config (YAML/JSON) to use for interceptor",
    )

    # Delete action parsers
    delete_interceptor_mapping_parser = interceptors_subparsers.add_parser(
        name="delete",
        help="Delete interceptor",
        parents=[USERNAME_PARSER],
    )
    delete_interceptor_mapping_parser.add_argument(
        "--interceptor-name",
        dest="interceptor_name",
        required=True,
        help="Interceptor name to delete as seen in the vCluster.",
    )
