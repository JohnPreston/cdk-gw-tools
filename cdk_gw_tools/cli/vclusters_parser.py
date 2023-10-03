# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from argparse import ArgumentParser

from .vclusters_interceptors_subparser import set_interceptors_actions_parsers

VCLUSTER_PARSER = ArgumentParser(add_help=False)
VCLUSTER_PARSER.add_argument(
    "--vcluster-name",
    dest="vcluster_name",
    required=True,
    help="Name of the vcluster to make operations for",
)


def set_vclusters_actions_parsers(vclusters_subparsers):
    """Creates all the parser and subparsers for vClusters API endpoints"""

    # List all
    list_parser = vclusters_subparsers.add_parser(
        name="list", help="List all vClusters"
    )

    # Auth / Token
    tenant_token = vclusters_subparsers.add_parser(
        name="auth",
        help="Create a new JWT for vCluster/Username",
        parents=[VCLUSTER_PARSER],
    )
    tenant_token_subparsers = tenant_token.add_subparsers(dest="sub_action")
    tenant_token_create_parser = tenant_token_subparsers.add_parser(name="create")
    tenant_token_create_parser.add_argument(
        "--lifetime-in-seconds",
        dest="token_lifetime_in_seconds",
        type=int,
        help="Token lifetime in seconds. Sets expiry. Defaults 1 day (86400)",
        default=86400,
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
    set_vcluster_mappings_actions(vclusters_subparsers)
    set_interceptors_actions_parsers(vclusters_subparsers)


def set_vcluster_mappings_actions(vclusters_subparsers):
    # Mappings
    mappings_parser = vclusters_subparsers.add_parser(
        name="mappings",
        help="Manages vCluster mappings",
        parents=[VCLUSTER_PARSER],
    )
    mappings_subparsers = mappings_parser.add_subparsers(dest="sub_action")
    list_parser = mappings_subparsers.add_parser(
        name="list",
        help="List vCluster mappings",
    )
    list_parser.add_argument(
        "--no-concentrated",
        action="store_true",
        help="Excludes concentrated topics from list",
        dest="no_concentrated",
        required=False,
    )
    list_parser.add_argument(
        "--mapped-only",
        action="store_true",
        help="Excludes concentrated topics & topics starting with the vcluster name",
        dest="mapped_only",
        required=False,
    )
    list_parser.add_argument(
        "--as-import-config",
        action="store_true",
        help="Returns the equivalent output to use with import-from-config",
    )
    create_parser = mappings_subparsers.add_parser(
        name="create",
        help="Create a new vCluster mapping",
    )
    create_parser.add_argument("--logical-topic-name", type=str, required=True)
    create_parser.add_argument("--physical-topic-name", type=str, required=True)
    create_parser.add_argument(
        "--read-only",
        required=False,
        default=False,
        dest="ReadOnly",
        action="store_true",
        help="Creates mapping in ReadOnly (defaults to Read-Write)",
    )
    create_parser.add_argument(
        "--concentrated",
        required=False,
        default=False,
        action="store_true",
        help="Create concentrated mapping",
    )
    create_parser.add_argument(
        "--cluster-id",
        type=str,
        required=False,
        help="Creates a mapping for merged cluster",
    )
    # Delete action parsers
    delete_all_mappings_parser = mappings_subparsers.add_parser(
        name="delete-all-mappings",
        help="Delete all topics mappings for a given vCluster",
        parents=[],
    )
    delete_topic_mapping_parser = mappings_subparsers.add_parser(
        name="delete-topic-mapping",
        help="Delete a topic mapping for a given vCluster",
        parents=[],
    )
    delete_topic_mapping_parser.add_argument(
        "--logical-topic-name",
        dest="logicalTopicName",
        required=True,
        help="Topic name as seen in the vCluster.",
    )

    # Custom actions
    import_from_vclusters_parser = mappings_subparsers.add_parser(
        name="import-from-vclusters-config",
        help="Create topic mappings from existing vclusters",
    )
    import_from_vclusters_parser.add_argument(
        "-f",
        "--import-config-file",
        dest="import_config_file",
        help="Path to the mappings import file",
        required=True,
        type=str,
    )
    import_from_vcluster_parser = mappings_subparsers.add_parser(
        name="import-from-vcluster",
        help="Import all topics from a existing vCluster",
        parents=[],
    )
    import_from_vcluster_parser.add_argument(
        "--src",
        "--source-vcluster",
        dest="source_vcluster",
        help="Name of the source vCluster to import the mappings from",
        type=str,
        required=True,
    )
