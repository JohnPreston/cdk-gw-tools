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


def set_vcluster_concentration_actions(vclusters_subparsers):
    # Concentration rules
    mappings_parser = vclusters_subparsers.add_parser(
        name="concentration-rules",
        help="Manages vCluster concentration rules",
        parents=[VCLUSTER_PARSER],
    )
    concentration_subparsers = mappings_parser.add_subparsers(dest="sub_action")

    list_parser = concentration_subparsers.add_parser(
        name="list",
        help="List vCluster concentration rules",
    )

    create_parser = concentration_subparsers.add_parser(
        name="create",
        help="Create a new vCluster mapping",
    )
    create_parser.add_argument("--pattern", type=str, required=True, dest="pattern")
    create_parser.add_argument(
        "--delete-topic-name", type=str, required=True, dest="deleteTopicName"
    )
    create_parser.add_argument(
        "--compact-topic-name", type=str, required=False, dest="compactTopicName"
    )
    create_parser.add_argument(
        "--delete-compact-topic-name",
        type=str,
        required=False,
        dest="deleteCompactTopicName",
    )
    create_parser.add_argument(
        "--cluster-id",
        type=str,
        required=False,
        help="Creates a mapping for merged cluster",
        dest="clusterId",
    )

    delete_topic_mapping_parser = concentration_subparsers.add_parser(
        name="delete",
        help="Delete a topic mapping for a given vCluster",
        parents=[],
    )
    delete_topic_mapping_parser.add_argument(
        "--pattern",
        dest="pattern",
        required=True,
        help="Pattern concentration rule to remove",
    )
