from typing import Collection, Dict, Iterable, List, Optional, Set

from di.core.assignment import (
    Assignment,
    AssignmentError,
    AssignmentFactorySelector,
    DirectAssignmentFactorySelector,
)
from di.core.element import Dependency, Element, Value
from di.core.injection.base import (
    AbstractInjectionSolver,
    InjectionGraph,
    InjectionGraphEdge,
    InjectionPlan,
    InjectionProblem,
    InjectionSolverAssignmentError,
    InjectionSolverCyclicDependencyError,
)
from di.utils.graph import (
    DirectionalGraph,
    DirectionalGraphIteratorError,
    DirectionalGraphTopologyIterator,
)


class _InjectionSolverCache:
    __slots__ = "_dependencies", "_cache"

    def __init__(self):
        self._dependencies: Dict[Element, Collection[Dependency]] = {}
        self._cache: Dict[Element, Value] = {}

    def dependencies(self, *elements: Element) -> Iterable[Dependency]:
        for element in elements:
            if element not in self._dependencies:
                self._dependencies[element] = [*element.dependencies()]
            yield from self._dependencies[element]

    def values(self, *elements: Element) -> Iterable[Value]:
        for element in elements:
            value = self.value(element)
            if value:
                yield value

    def value(self, element: Element) -> Value:
        if element not in self._cache:
            self._cache[element] = element.value()
        return self._cache[element]


class InjectionSolver(AbstractInjectionSolver):
    def __init__(self, factory_selector: Optional[AssignmentFactorySelector] = None):
        self._cache = _InjectionSolverCache()
        self._factory_selector = factory_selector or DirectAssignmentFactorySelector()

    def solve(self, problem: InjectionProblem) -> InjectionPlan:
        assignments = [*self._iterate_assignments(problem)]
        graph = self._create_graph([*problem.imports, *problem.elements], assignments)
        stages = self._create_stages(graph)
        return InjectionPlan(
            assignments=assignments,
            graph=graph,
            stages=stages,
        )

    def _iterate_assignments(self, problem: InjectionProblem):
        selector = self._factory_selector
        values = {*self._cache.values(*problem.imports, *problem.elements)}
        for dependency in self._cache.dependencies(*problem.elements):
            factory = selector.select(dependency)
            try:
                assignment = factory.assign(dependency, values)
                if assignment:
                    yield assignment
            except AssignmentError as error:
                raise InjectionSolverAssignmentError(dependency, str(error))

    @classmethod
    def _create_graph(
        cls, elements: Iterable[Element], assignments: Iterable[Assignment]
    ) -> InjectionGraph:
        return DirectionalGraph(
            nodes=elements,
            edges=cls._create_graph_edges(assignments),
        )

    @classmethod
    def _create_graph_edges(cls, assignments: Iterable[Assignment]):
        for assignment in assignments:
            for value in assignment.values:
                yield InjectionGraphEdge(assignment.dependency, value)

    @staticmethod
    def _create_stages(graph: InjectionGraph) -> List[Set[Element]]:
        try:
            return [*DirectionalGraphTopologyIterator(graph)]
        except DirectionalGraphIteratorError:
            raise InjectionSolverCyclicDependencyError
