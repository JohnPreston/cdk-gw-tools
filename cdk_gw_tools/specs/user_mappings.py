# generated by datamodel-codegen:
#   filename:  user-mappings.spec.json
#   timestamp: 2023-12-04T17:06:08+00:00

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

Identities = List[str]


@dataclass
class UserMappings:
    identities: Identities


@dataclass
class UserMappingsConfig:
    userMappings: Optional[Dict[str, UserMappings]] = None
