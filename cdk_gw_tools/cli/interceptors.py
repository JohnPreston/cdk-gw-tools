# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from argparse import ArgumentParser

VCLUSTER_PARSER = ArgumentParser(add_help=False)
VCLUSTER_PARSER.add_argument(
    "--vcluster-name",
    dest="vcluster_name",
    required=False,
    help="Name of the vCluster to make operations for",
)

USERNAME_PARSER = ArgumentParser(add_help=False)
USERNAME_PARSER.add_argument(
    "--username",
    dest="username",
    required=False,
    help="Specify username to get interceptors for",
)
GROUP_PARSER = ArgumentParser(add_help=False)
GROUP_PARSER.add_argument(
    "--group",
    dest="group",
    required=False,
    help="Specify username to get interceptors for",
)


def set_interceptors_actions_parsers(interceptors_subparsers):
    """Creates all the parser and subparsers for GW API endpoints"""
    list_all_parser = interceptors_subparsers.add_parser(
        name="list-all",
        help="List all the interceptors on GW for all contexts",
    )

    list_parser = interceptors_subparsers.add_parser(
        name="list",
        help="List interceptors",
        parents=[USERNAME_PARSER, VCLUSTER_PARSER, GROUP_PARSER],
    )
    list_parser.add_argument(
        "--global",
        action="store_true",
        help="List global interceptors.",
        dest="is_global",
    )

    create_parser = interceptors_subparsers.add_parser(
        name="create-update",
        help="Create or update a new vCluster mapping",
        parents=[USERNAME_PARSER, VCLUSTER_PARSER, GROUP_PARSER],
    )
    create_parser.add_argument(
        "--interceptor-name",
        dest="interceptor_name",
        required=True,
        help="Name of the interceptor to create or update",
    )
    create_parser.add_argument(
        "--global",
        action="store_true",
        help="Create or update a global interceptor",
        dest="is_global",
    )
    create_parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to config (YAML/JSON) to use for interceptor",
        dest="config_file_path",
    )

    # Delete action parsers
    delete_interceptor_mapping_parser = interceptors_subparsers.add_parser(
        name="delete",
        help="Delete interceptor",
        parents=[USERNAME_PARSER, VCLUSTER_PARSER, GROUP_PARSER],
    )
    delete_interceptor_mapping_parser.add_argument(
        "--interceptor-name",
        dest="interceptor_name",
        required=True,
        help="Interceptor name to delete as seen in the vCluster.",
    )
    delete_interceptor_mapping_parser.add_argument(
        "--global",
        action="store_true",
        help="Delete global interceptor",
        dest="is_global",
    )
    import_from_config_parser = interceptors_subparsers.add_parser(
        name="import-from-config",
        help="Import interceptors from config file",
    )
    import_from_config_parser.add_argument(
        "-f",
        "--config-file",
        dest="config_file_path",
        type=str,
        help="Path to the config file (YAML)",
        required=True,
    )
