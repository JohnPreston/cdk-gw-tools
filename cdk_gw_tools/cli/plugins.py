# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations


def set_plugings_actions_parsers(plugins_subparsers):
    list_parser = plugins_subparsers.add_parser(name="list", help="List all plugins")
    list_parser.add_argument("--extended", action="store_true", default=False)
    list_parser.add_argument(
        "--as-list", action="store_true", default=False, help="Returns only the list"
    )
