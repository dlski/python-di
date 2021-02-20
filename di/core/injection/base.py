from dataclasses import dataclass
from typing import Collection, Sequence

from di.core.assignment import Assignment
from di.core.element import Dependency, Element, Value
from di.utils.graph import DirectionalGraph, DirectionalGraphEdge


@dataclass
class InjectionProblem:
    imports: Collection[Element]
    elements: Collection[Element]


class InjectionGraphEdge(DirectionalGraphEdge[Element]):
    __slots__ = "source", "target"

    def __init__(self, dependency: Dependency, value: Value):
        self.source = dependency.source
        self.target = value.source


InjectionGraph = DirectionalGraph[Element, InjectionGraphEdge]


@dataclass
class InjectionPlan:
    assignments: Collection[Assignment]
    graph: InjectionGraph
    stages: Sequence[Collection[Element]]


class InjectionSolverError(Exception):
    pass


class InjectionSolverAssignmentError(InjectionSolverError):
    def __init__(self, dependency: Dependency, msg: str):
        super().__init__(msg)
        self.dependency = dependency


class InjectionSolverCyclicDependencyError(InjectionSolverError):
    pass


class AbstractInjectionSolver:
    def solve(self, problem: InjectionProblem) -> InjectionPlan:
        raise NotImplementedError
