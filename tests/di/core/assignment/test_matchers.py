from typing import Iterable, List

from di.core.assignment import (
    DirectMatcher,
    TypeAggregationMatcher,
    TypeIterableMatcher,
    TypeMatcher,
)
from di.core.element import Dependency, Element, Value


def test_direct_matcher():
    d = Dependency(source=..., arg="test", type=float)
    v1 = Value(source=..., type=int)
    v2 = Value(source=..., type=int)
    v3 = Value(source=..., type=float)
    v_set = {v1, v2, v3}
    v_sub_set = {v1, v2}
    matcher = DirectMatcher(
        {
            d: v_set,
        }
    )
    v_visited = set()
    for value in matcher.iterate(d, v_sub_set):
        assert value in v_sub_set
        v_visited.add(value)
    assert v_visited == v_sub_set


class X:
    pass


class X1(X):
    pass


class Y:
    pass


def _e() -> Element:
    return Element(
        injector=...,
        strategy=...,
    )


def _same_type_dv(type_):
    d = Dependency(source=_e(), arg="test", type=type_)
    v = Value(source=_e(), type=type_)
    return d, v


def test_type_matcher():
    type_matcher = TypeMatcher()

    d, v = _same_type_dv(int)
    for _ in type_matcher.iterate(d, {v}):
        raise AssertionError

    d = Dependency(source=_e(), arg="test", type=X)
    v1 = Value(source=_e(), type=X1)
    v2 = Value(source=_e(), type=Y)
    assert list(type_matcher.iterate(d, {v1, v2})) == [v1]
    d.source = v1.source = v2.source = _e()
    assert list(type_matcher.iterate(d, {v1, v2})) == []


def test_iterable_matcher():
    iterable_matcher = TypeIterableMatcher()

    d, v = _same_type_dv(int)
    assert [*iterable_matcher.iterate(d, {v})] == []

    d, v = _same_type_dv(List[int])
    assert [*iterable_matcher.iterate(d, {v})] == []

    d = Dependency(source=_e(), arg="test", type=X)
    v1 = Value(source=_e(), type=X1)
    v2 = Value(source=_e(), type=Y)
    assert [*iterable_matcher.iterate(d, {v1, v2})] == []

    # noinspection PyTypeChecker
    d = Dependency(source=_e(), arg="test", type=List[X])
    # noinspection PyTypeChecker
    v1 = Value(source=_e(), type=Iterable[X1])
    # noinspection PyTypeChecker
    v2 = Value(source=_e(), type=List[Y])
    assert [*iterable_matcher.iterate(d, {v1, v2})] == [v1]
    d.source = v1.source = v2.source = _e()
    assert [*iterable_matcher.iterate(d, {v1, v2})] == []


def test_aggregation_matcher():
    aggregation_matcher = TypeAggregationMatcher()

    for type_ in [int, X, List[int], List[X]]:
        d, v = _same_type_dv(type_)
        assert [*aggregation_matcher.iterate(d, {v})] == []

    # noinspection PyTypeChecker
    d = Dependency(source=_e(), arg="test", type=List[int])
    # noinspection PyTypeChecker
    v = Value(source=_e(), type=int)
    assert [*aggregation_matcher.iterate(d, {v})] == []

    # noinspection PyTypeChecker
    d = Dependency(source=_e(), arg="test", type=List[X])
    # noinspection PyTypeChecker
    v1 = Value(source=_e(), type=X1)
    # noinspection PyTypeChecker
    v2 = Value(source=_e(), type=Y)
    assert [*aggregation_matcher.iterate(d, {v1, v2})] == [v1]
    d.source = v1.source = v2.source = _e()
    assert [*aggregation_matcher.iterate(d, {v1, v2})] == []
