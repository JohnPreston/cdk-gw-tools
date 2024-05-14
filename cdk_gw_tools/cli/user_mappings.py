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


def set_user_mappings_actions_parsers(user_mappings_sub_parsers):
    list_parser = user_mappings_sub_parsers.add_parser(
        name="list",
        help="List user mappings",
        parents=[VCLUSTER_PARSER],
    )
    list_parser.add_argument(
        "--detailed",
        required=False,
        help="Returns the full list of identities with details",
        action="store_true",
        default=False,
        dest="detailed",
    )
    describe_parser = user_mappings_sub_parsers.add_parser(
        name="describe",
        help="Describe user mapping",
        parents=[VCLUSTER_PARSER],
    )
    describe_parser.add_argument(
        "--username",
        required=True,
        help="Username of the identity",
    )
    create_parser = user_mappings_sub_parsers.add_parser(
        name="create",
        help="Create user mapping",
        parents=[VCLUSTER_PARSER],
    )
    create_parser.add_argument(
        "--group",
        required=False,
        action="append",
        help="Groups this user is to be added into",
        default=[],
    )

    create_parser.add_argument(
        "--username",
        required=True,
        help="Friendly username.",
    )
    create_parser.add_argument(
        "--principal",
        required=True,
        help="Value of the `principal` used for Kafka authentication. When using OAuth, that's usuall the claims.sub value.",
    )

    delete_parser = user_mappings_sub_parsers.add_parser(
        name="delete",
        help="Create user mapping for vCluster",
        parents=[VCLUSTER_PARSER],
    )
    delete_parser.add_argument(
        "--username",
        required=True,
        help="Value of the `sub` of the JWT token from your issuer",
    )


def set_gw_user_mappings_actions_parsers(gw_user_mappings_subparsers):
    import_parser = gw_user_mappings_subparsers.add_parser(
        name="import", help="Import user-mappings from config-file"
    )
    import_parser.add_argument(
        "-f",
        "--config-file",
        dest="import_file",
        type=str,
        help="Path to the import config file",
    )
    import_parser.add_argument(
        "--remove-unset",
        action="store_true",
        help="If true, remove mappings on GW not defined in the config file",
    )

    export_parser = gw_user_mappings_subparsers.add_parser(
        name="export", help="Export user-mappings from config-file"
    )
    export_parser.add_argument(
        "-f",
        "--config-file",
        dest="import_file",
        type=str,
        help="Path to the import config file",
        required=False,
    )
