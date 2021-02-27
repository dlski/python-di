from typing import Iterable, Sequence, Set

import pytest

from di.core.assignment import AssignmentFactory, DirectAssignmentFactorySelector
from di.core.element import Dependency, Element
from di.core.injection import (
    InjectionProblem,
    InjectionSolver,
    InjectionSolverAssignmentError,
    InjectionSolverCyclicDependencyError,
)


def test_injection_unsatisfied(
    unsatisfied_elements: Sequence[Element],
):
    imports = unsatisfied_elements[:1]
    elements = unsatisfied_elements[1:]
    solver = InjectionSolver()
    with pytest.raises(InjectionSolverAssignmentError) as result:
        solver.solve(InjectionProblem(imports=imports, elements=elements))
    error = result.value
    assert error.dependency.arg == "x"


def test_injection_cycle(
    cycle_elements: Sequence[Element],
):
    solver = InjectionSolver()
    with pytest.raises(InjectionSolverCyclicDependencyError):
        solver.solve(InjectionProblem(imports=[], elements=cycle_elements))


def test_injection_satisfied(
    simple_elements: Sequence[Element],
):
    imports = simple_elements[:1]
    elements = simple_elements[1:]
    solver = InjectionSolver()
    plan = solver.solve(InjectionProblem(imports=imports, elements=elements))
    for index in range(3):
        assert (
            len(plan.stages[index]) == 1
            and simple_elements[index] in plan.stages[index]
        )


class VisitedDirectAssignmentFactorySelector(DirectAssignmentFactorySelector):
    def __init__(self):
        super().__init__()
        self.visited_args: Set[str] = set()

    def select(self, dependency: Dependency) -> AssignmentFactory:
        self.visited_args.add(dependency.arg)
        return super().select(dependency)

    @classmethod
    def iterate_args(cls, _elements: Iterable[Element]):
        for e in _elements:
            for dependency in e.dependencies():
                yield dependency.arg


def test_injection_selector_used(
    simple_elements: Sequence[Element],
):
    factory_selector = VisitedDirectAssignmentFactorySelector()

    imports = simple_elements[:1]
    elements = simple_elements[1:]
    solver = InjectionSolver(factory_selector=factory_selector)
    solver.solve(InjectionProblem(imports=imports, elements=elements))
    assert factory_selector.visited_args == {
        *VisitedDirectAssignmentFactorySelector.iterate_args(elements)
    }
