import itertools
from typing import Collection, FrozenSet, Iterable, Optional, Sequence, Set, Tuple

import pytest

from di.core.assignment import (
    AggregationAssignmentFactory,
    AssignmentError,
    DirectAssignmentFactory,
    MixedIterableValuesMapper,
)
from di.core.element import (
    Dependency,
    Element,
    InjectionResult,
    Injector,
    InjectorDependency,
    Value,
)


def _dependencies_values(
    elements: Sequence[Element],
    imports: Sequence[Element] = (),
) -> Tuple[Sequence[Dependency], Set[Value]]:
    dependencies = list(itertools.chain(*(e.dependencies() for e in elements)))
    values = {e.value() for e in [*elements, *imports]}
    return dependencies, values


def test_direct_assignment_factory(
    unsatisfied_elements: Sequence[Element],
    simple_elements: Sequence[Element],
    redundant_elements: Sequence[Element],
    same_input_output_elements: Sequence[Element],
):
    factory = DirectAssignmentFactory()

    dependencies, values = _dependencies_values(unsatisfied_elements)
    with pytest.raises(AssignmentError):
        for dependency in dependencies:
            factory.assign(dependency, values)

    dependencies, values = _dependencies_values(simple_elements)
    for dependency in dependencies:
        assignment = factory.assign(dependency, values)
        assert not dependency.mandatory or assignment
        if assignment:
            assert len(assignment.values) == 1

    dependencies, values = _dependencies_values(redundant_elements)
    with pytest.raises(AssignmentError):
        for dependency in dependencies:
            factory.assign(dependency, values)

    dependencies, values = _dependencies_values(same_input_output_elements)
    with pytest.raises(AssignmentError):
        for dependency in dependencies:
            factory.assign(dependency, values)


class MockupInjector(Injector):
    def __init__(self, dependency_types: Collection, result_type=None):
        self.dependency_types = dependency_types
        self.result_type = result_type

    def __call__(self, *args, **kwargs):
        raise AssertionError

    def dependencies(self) -> Iterable[InjectorDependency]:
        return [
            InjectorDependency(
                arg=f"arg{index}",
                type=type_,
            )
            for index, type_ in enumerate(self.dependency_types)
        ]

    def result(self) -> Optional[InjectionResult]:
        return InjectionResult(type=self.result_type)


def test_aggregation_assignment_factory():
    class X:
        pass

    class Y(X):
        pass

    class Z(X):
        pass

    class T:
        pass

    x, x_agg, y, z, t, t_inv = (
        Element(injector=MockupInjector([FrozenSet[X]]), strategy=...),
        Element(injector=MockupInjector([], Iterable[X]), strategy=...),
        Element(injector=MockupInjector([], Y), strategy=...),
        Element(injector=MockupInjector([], Z), strategy=...),
        Element(injector=MockupInjector([], T), strategy=...),
        Element(injector=MockupInjector([T]), strategy=...),
    )

    factory = AggregationAssignmentFactory()

    dependencies, values = _dependencies_values([x, t])
    assignments = [factory.assign(dependency, values) for dependency in dependencies]
    assert len(assignments) == 1
    assert len(assignments[0].values) == 0

    dependencies, values = _dependencies_values([t_inv, t])
    with pytest.raises(AssignmentError):
        for dependency in dependencies:
            factory.assign(dependency, values)

    dependencies, values = _dependencies_values([x, y, z, t], imports=[x_agg])
    assignments = [factory.assign(dependency, values) for dependency in dependencies]
    assert len(assignments) == 1
    assignment = assignments[0]
    assert len(assignment.values) == 3
    assert {value.type for value in assignment.values} == {
        e.value().type for e in [x_agg, y, z]
    }

    mapper = assignment.mapper
    assert isinstance(mapper, MixedIterableValuesMapper)
    assert mapper.container_factory is frozenset
    for value, flag in zip(assignment.values, mapper.iterate_args):
        if hasattr(value.type, "__origin__"):
            assert flag
        else:
            assert not flag
