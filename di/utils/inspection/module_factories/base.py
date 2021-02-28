from types import ModuleType
from typing import Any, Collection, Iterable, Tuple

FactoryItem = Tuple[str, Any]


class FactoryFilter:
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        raise NotImplementedError


class FactoryFilterCascade:
    def __init__(self, filters: Collection[FactoryFilter]):
        self.filters = filters

    def apply(self, module: ModuleType, items: Iterable[FactoryItem]):
        for filter_ in self.filters:
            items = [*filter_.filter(module, items)]
        return items
