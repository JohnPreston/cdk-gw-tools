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
