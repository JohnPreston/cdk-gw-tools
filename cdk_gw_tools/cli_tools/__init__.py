#   SPDX-License-Identifier: Apache-2.0
#   Copyright 2023 John Mille <john@ews-network.net>

from __future__ import annotations

from typing import Union

import yaml

try:
    from yaml import Loader
except ImportError:
    from yaml import CLoader as Loader

import json
from os import path


def load_config_file(file_path: str) -> Union[dict, list]:
    """Simple function to load a file and return dict/list, the best effort to use YAML or JSON. If neither, fails."""
    with open(path.abspath(file_path)) as file_fd:
        content = file_fd.read()

    try:
        return yaml.load(content, Loader=Loader)
    except yaml.YAMLError:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"The content of {file_path} is neither a valid YAML or JSON")
