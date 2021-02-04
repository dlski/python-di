from typing import Collection, Dict, Iterable, Set

from di.core.assignment.base import Matcher
from di.core.element import Dependency, Value
from di.utils.inspection import aggregated_type, is_base_type, is_compatible_type


class DirectMatcher(Matcher):
    def __init__(self, map_: Dict[Dependency, Collection[Value]]):
        self.map = map_

    def iterate(self, dependency: Dependency, values: Set[Value]) -> Iterable[Value]:
        if dependency in self.map:
            for map_value in self.map[dependency]:
                if map_value in values:
                    yield map_value


class BaseTypeMatcher(Matcher):
    def iterate(self, dependency: Dependency, values: Set[Value]) -> Iterable[Value]:
        if is_base_type(dependency.type):
            return
        for value in values:
            if is_base_type(value.type):
                continue
            if dependency.source == value.source:
                continue
            yield value


class TypeMatcher(BaseTypeMatcher):
    def iterate(self, dependency: Dependency, values: Set[Value]) -> Iterable[Value]:
        for value in super().iterate(dependency, values):
            if is_compatible_type(value.type, dependency.type):
                yield value


class TypeIterableMatcher(BaseTypeMatcher):
    def iterate(self, dependency: Dependency, values: Set[Value]) -> Iterable[Value]:
        nested_model = aggregated_type(dependency.type)
        if not nested_model:
            return
        for value in super().iterate(dependency, values):
            if is_compatible_type(aggregated_type(value.type), nested_model):
                yield value


class TypeAggregationMatcher(BaseTypeMatcher):
    def iterate(self, dependency: Dependency, values: Set[Value]) -> Iterable[Value]:
        nested_model = aggregated_type(dependency.type)
        if not nested_model:
            return
        for value in super().iterate(dependency, values):
            if is_compatible_type(value.type, nested_model):
                yield value
