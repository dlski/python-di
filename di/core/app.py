from dataclasses import dataclass, field
from typing import Set

from di.core.element import Element
from di.core.module.base import Module


@dataclass
class Application:
    modules: Set[Module] = field(default_factory=set)

    @property
    def elements(self) -> Set[Element]:
        all_set = set()
        for module in self.modules:
            all_set.update(module.elements)
        return all_set


class ApplicationRelated:
    app: Application
