from typing import Collection, List, Optional

from di.core.assignment.base import AssignmentFactory, AssignmentFactorySelector
from di.core.assignment.factories import (
    AggregationAssignmentFactory,
    DirectAssignmentFactory,
)
from di.core.element import Dependency, Element
from di.utils.inspection import aggregated_type, is_compatible_type


class DependencyCheck:
    def applies_to(self, dependency: Dependency) -> bool:
        raise NotImplementedError


class AggTypeDependencyCheck(DependencyCheck):
    def __init__(self, type_spec):
        self.type_spec = type_spec

    def applies_to(self, dependency: Dependency):
        type_ = aggregated_type(dependency.type)
        if type_:
            return is_compatible_type(type_, self.type_spec)


class ArgDependencyCheck(DependencyCheck):
    def __init__(self, element: Element, arg: str):
        self.element = element
        self.arg = arg

    def applies_to(self, dependency: Dependency):
        return self.element == dependency.source and self.arg == dependency.arg


class AggregationAssignmentFactorySelector(AssignmentFactorySelector):
    def __init__(
        self, aggregation_checks: Optional[Collection[DependencyCheck]] = None
    ):
        self._aggregation_checks: List[DependencyCheck] = [*(aggregation_checks or ())]
        self._direct_factory = DirectAssignmentFactory()
        self._aggregation_factory = AggregationAssignmentFactory()

    def add_aggregation_check(self, check: DependencyCheck):
        self._aggregation_checks.append(check)

    def select(self, dependency: Dependency) -> AssignmentFactory:
        for check in self._aggregation_checks:
            if check.applies_to(dependency):
                return self._aggregation_factory
        return self._direct_factory
