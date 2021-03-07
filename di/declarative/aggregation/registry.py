from collections import defaultdict
from typing import Collection, DefaultDict, Dict, Iterable, List, Tuple

from di.core.element import Element
from di.core.module import Module
from di.declarative.aggregation.checks import IsAggregationType
from di.declarative.aggregation.selector import AggAssigmentFactorySelector


class AggRegistry:
    def __init__(self):
        self._app_checks: List[IsAggregationType] = []
        self._module_checks: DefaultDict[Module, List[IsAggregationType]] = defaultdict(
            list
        )
        self._element_checks: DefaultDict[
            Element, List[IsAggregationType]
        ] = defaultdict(list)

    def include_globals(self, checks: Iterable[IsAggregationType]):
        self._app_checks.extend(checks)

    def add_module(self, module: Module, checks: Iterable[IsAggregationType]):
        self._module_checks[module].extend(checks)

    def include_elements(
        self, iterable: Iterable[Tuple[Element, Collection[IsAggregationType]]]
    ):
        for element, checks in iterable:
            self._element_checks[element].extend(checks)

    def build_selector(self) -> AggAssigmentFactorySelector:
        element_map: Dict[Element, List[IsAggregationType]] = defaultdict(list)
        for element, checks in self._element_checks.items():
            element_map[element] = [*checks]
        for module, checks in self._module_checks.items():
            for element in module.elements:
                element_map[element].extend(checks)
        return AggAssigmentFactorySelector(
            element_map=element_map,
            global_=[*self._app_checks],
        )
