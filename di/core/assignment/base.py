from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Set

from di.core.element import Dependency, Value


class Matcher:
    def iterate(self, dependency: Dependency, values: Set[Value]) -> Iterable[Value]:
        raise NotImplementedError


class ValuesMapper:
    def map(self, objects: Sequence):
        raise NotImplementedError


@dataclass
class Assignment:
    mapper: ValuesMapper
    dependency: Dependency
    values: Sequence[Value]


class AssignmentError(Exception):
    pass


class AssignmentFactory:
    def assign(
        self, dependency: Dependency, values: Set[Value]
    ) -> Optional[Assignment]:
        raise NotImplementedError


class AssignmentFactorySelector:
    def select(self, dependency: Dependency) -> AssignmentFactory:
        raise NotImplementedError
