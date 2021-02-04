from typing import (
    Collection,
    Dict,
    FrozenSet,
    Iterable,
    List,
    NewType,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from di.utils.inspection import (
    aggregated_type,
    aggregation_type_factory,
    is_base_type,
    is_compatible_type,
)


class SomeClass:
    pass


def test_is_base_type():
    assert is_base_type(str)
    assert is_base_type(NewType("TestStr", str))
    assert is_base_type(int)
    assert is_base_type(list)
    assert is_base_type(List)
    assert is_base_type(List[str])
    assert is_base_type(List[Set[int]])
    assert is_base_type(Collection[str])
    assert is_base_type(Dict[str, int])
    assert not is_base_type(NewType("SomeClassEx", SomeClass))
    assert not is_base_type(List[SomeClass])
    assert not is_base_type(List[Set[SomeClass]])
    assert not is_base_type(Collection[SomeClass])
    assert not is_base_type(Dict[str, SomeClass])
    assert not is_base_type(Dict[SomeClass, int])


def test_is_compatible_type():
    class X:
        pass

    class Y(X):
        pass

    class Z:
        pass

    assert not is_compatible_type(None, None)
    assert not is_compatible_type(None, X)
    assert not is_compatible_type(X, None)

    assert is_compatible_type(X, X)
    assert not is_compatible_type(X, Y)
    assert is_compatible_type(Y, X)

    assert is_compatible_type(List[X], Collection[X])
    assert is_compatible_type(Set[X], Collection[X])
    assert not is_compatible_type(Collection[X], List[X])
    assert not is_compatible_type(Collection[X], Set[X])

    assert is_compatible_type(List[Y], List[X])
    assert not is_compatible_type(List[X], List[Y])

    assert is_compatible_type(List[List[Y]], List[List[X]])
    assert not is_compatible_type(List[List[X]], List[List[Y]])
    assert is_compatible_type(List[Set[X]], List[Collection[X]])
    assert not is_compatible_type(List[Set[X]], List[Collection[Y]])
    assert is_compatible_type(Dict[str, Y], Dict[str, X])
    assert not is_compatible_type(Dict[str, X], Dict[str, Y])

    assert is_compatible_type(List[X], Optional[List[X]])
    assert not is_compatible_type(Optional[List[X]], List[X])
    assert not is_compatible_type(List[X], Optional[List[Y]])

    assert is_compatible_type(Union[X, Y], Union[X, Y])
    assert is_compatible_type(Union[X, Y], Union[X, Z])
    assert not is_compatible_type(Union[X, Z], Union[X, Y])
    assert is_compatible_type(X, Union[X, Y])
    assert is_compatible_type(Union[X, Y], X)
    assert not is_compatible_type(Union[X, Z], X)
    assert not is_compatible_type(Union[X, Y], Y)


def test_aggregated_type():
    class X:
        pass

    class Y(X):
        pass

    class Z:
        pass

    t = TypeVar("t", bound=X)
    assert aggregated_type(None) is None
    assert aggregated_type(X) is None
    assert aggregated_type(List[t]) is t
    assert aggregated_type(Dict[X, X]) is None
    assert aggregated_type(List[X]) == X
    assert aggregated_type(Iterable[X]) == X
    assert aggregated_type(Iterable[Union[X, Y]]) == Union[X, Y]
    assert aggregated_type(Union[Iterable[X], Collection[Y]]) == Union[X, Y]
    assert aggregated_type(Union[Iterable[X], Set[Union[X, Z]], Y]) == Union[X, Z]


def test_aggregation_type_factory():
    assert aggregation_type_factory(List[str]) is list
    assert aggregation_type_factory(Collection[str]) is list
    assert aggregation_type_factory(Iterable[str]) is list
    assert aggregation_type_factory(Set[str]) is set
    assert aggregation_type_factory(FrozenSet[str]) is frozenset
    assert aggregation_type_factory(Tuple[str]) is tuple

    assert aggregation_type_factory(Optional[Set[str]]) is set
    assert aggregation_type_factory(Optional[Optional[Iterable[str]]]) is list
