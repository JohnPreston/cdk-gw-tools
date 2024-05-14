#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

import sys

try:
    from yaml import Dumper
except ImportError:
    from yaml import CDumper as Dumper

from cdk_gw_tools.cli_actions import main

if __name__ == "__main__":
    sys.exit(main())
