from typing import Optional, Set

from di.core.assignment.base import Assignment, AssignmentError, AssignmentFactory
from di.core.assignment.mappers import MixedIterableValuesMapper, SingleValuesMapper
from di.core.assignment.matchers import (
    TypeAggregationMatcher,
    TypeIterableMatcher,
    TypeMatcher,
)
from di.core.element import Dependency, Value
from di.utils.inspection import aggregated_type, aggregation_type_factory


class DirectAssignmentFactory(AssignmentFactory):
    def __init__(self):
        self._type_matcher = TypeMatcher()

    def assign(
        self, dependency: Dependency, values: Set[Value]
    ) -> Optional[Assignment]:
        matched_values = [*self._type_matcher.iterate(dependency, values)]
        if not matched_values:
            if dependency.mandatory:
                raise AssignmentError(f"No match for mandatory {dependency}")
            else:
                return None
        elif len(matched_values) > 1:
            raise AssignmentError(
                f"More than one match for {dependency}: {matched_values}"
            )
        return Assignment(
            mapper=SingleValuesMapper(),
            dependency=dependency,
            values=matched_values,
        )


class AggregationAssignmentFactory(AssignmentFactory):
    def __init__(self):
        self._iterable_matcher = TypeIterableMatcher()
        self._aggregation_matcher = TypeAggregationMatcher()

    def assign(
        self, dependency: Dependency, values: Set[Value]
    ) -> Optional[Assignment]:
        nested_type = aggregated_type(dependency.type)
        if not nested_type:
            raise AssignmentError(
                f"Type {dependency.type} is not a valid aggregation type"
            )

        iterable_values = [*self._iterable_matcher.iterate(dependency, values)]
        aggregated_values = [*self._aggregation_matcher.iterate(dependency, values)]
        all_values = iterable_values + aggregated_values
        iterate_args = [True] * len(iterable_values) + [False] * len(aggregated_values)
        return Assignment(
            mapper=MixedIterableValuesMapper(
                container_factory=aggregation_type_factory(dependency.type),
                iterate_args=iterate_args,
            ),
            dependency=dependency,
            values=all_values,
        )
