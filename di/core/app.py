from dataclasses import dataclass, field
from typing import Set

from di.core.module.base import Module


@dataclass
class Application:
    modules: Set[Module] = field(default_factory=set)
