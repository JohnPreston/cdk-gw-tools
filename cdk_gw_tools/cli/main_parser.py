# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from argparse import ArgumentParser
from os import environ

from cdk_gw_tools.cli.gw_parsers.plugins import set_plugings_actions_parsers
from cdk_gw_tools.cli.gw_parsers.user_mappings import (
    set_gw_user_mappings_actions_parsers,
)
from cdk_gw_tools.cli.vclusters_parser import set_vclusters_actions_parsers


def set_parser():
    main_parser = ArgumentParser("CDK Proxy CLI", add_help=True)
    main_parser.add_argument(
        "--format",
        "--output-format",
        dest="output_format",
        help="output format",
        default="yaml",
    )
    main_parser.add_argument(
        "--log-level", dest="loglevel", type=str, help="Set loglevel", required=False
    )
    main_parser.add_argument("--url", required=False)
    main_parser.add_argument("--username", required=False)
    main_parser.add_argument("--password", required=False)
    main_parser.add_argument(
        "-c",
        "--config-file",
        type=str,
        help="Path to the profiles files",
        default="{}/.cdk_gw.yaml".format(environ.get("HOME", ".")),
    )
    main_parser.add_argument(
        "-p",
        "--profile-name",
        type=str,
        help="Name of the profile to use to make API Calls",
    )

    cmd_parser = main_parser.add_subparsers(dest="category", help="Resources to manage")
    vclusters_parser = cmd_parser.add_parser(
        name="vclusters",
        help="Manages vClusters",
    )
    vclusters_subparsers = vclusters_parser.add_subparsers(
        dest="action", help="vCluster management"
    )
    set_vclusters_actions_parsers(vclusters_subparsers)

    plugins_parser = cmd_parser.add_parser(name="plugins", help="Manage plugins")
    plugins_subparsers = plugins_parser.add_subparsers(
        dest="action", help="Manage plugins actions"
    )
    set_plugings_actions_parsers(plugins_subparsers)

    gw_user_mappings_parser = cmd_parser.add_parser(
        name="user-mappings", help="Manage user mappings at the GW level"
    )
    gw_user_mappings_subparsers = gw_user_mappings_parser.add_subparsers(
        dest="action", help="Manage GW user mappings actions"
    )
    set_gw_user_mappings_actions_parsers(gw_user_mappings_subparsers)

    return main_parser
