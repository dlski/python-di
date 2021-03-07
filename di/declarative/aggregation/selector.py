from typing import Collection, Mapping

from di.core.assignment import (
    AggregationAssignmentFactory,
    AssignmentFactory,
    AssignmentFactorySelector,
    DirectAssignmentFactory,
)
from di.core.element import Dependency, Element
from di.declarative.aggregation.checks import IsAggregationType


class AggAssigmentFactorySelector(AssignmentFactorySelector):
    def __init__(
        self,
        element_map: Mapping[Element, Collection[IsAggregationType]],
        global_: Collection[IsAggregationType],
    ):
        self._direct = DirectAssignmentFactory()
        self._agg = AggregationAssignmentFactory()

        self._element = element_map
        self._global = global_

    def select(self, dependency: Dependency) -> AssignmentFactory:
        for check in self._element.get(dependency.source, ()):
            if check(dependency):
                return self._agg
        for check in self._global:
            if check(dependency):
                return self._agg
        return self._direct
