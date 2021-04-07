from typing import Any, Generic, List, TypeVar

from di.utils.inspection import FactoryInspection


class SomeClass:
    def __init__(self, x: str, y: bool = False, *, a: list, b: tuple = (), c):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.c = c


def some_function(x: str, y: bool = False, *, a: list, b: tuple = (), c) -> set:
    print(x, y, a, b, c)
    return set()


def some_fwd_ref_annotation(c: "SomeClass") -> "SomeClass":
    return c


def some_nested_fwd_ref_annotation(d: List[List["SomeClass"]]) -> List["SomeClass"]:
    return d and d[0] or []


all_args = list("xyabc")
all_annotations = {
    "x": str,
    "y": bool,
    "a": list,
    "b": tuple,
}


def test_factory_type_inspection():
    inspection = FactoryInspection(SomeClass)

    args = inspection.args
    assert "self" not in args, "self in args"
    assert all(arg in args for arg in all_args), "not all args inspected"

    annotations = inspection.args_annotations
    assert all(
        annotations.get(name) == clazz for name, clazz in annotations.items()
    ), "annotations not consistent"

    assert inspection.return_type == SomeClass


def test_factory_fn_inspection():
    inspection = FactoryInspection(some_function)

    args = inspection.args
    assert all(arg in args for arg in all_args), "not all args inspected"

    annotations = inspection.args_annotations
    assert all(
        annotations.get(name) == clazz for name, clazz in annotations.items()
    ), "annotations not consistent"

    assert inspection.return_type == set


def test_factory_fwd_ref_annotation_inspection():
    inspection = FactoryInspection(some_fwd_ref_annotation)
    assert inspection.args_annotations["c"] == SomeClass
    assert inspection.return_type == SomeClass


def test_factory_nested_fwd_ref_annotation_inspection():
    def _ensure_list_and_get_arg(_t: Any):
        assert _t
        assert hasattr(_t, "__origin__") and _t.__origin__ is list
        assert hasattr(_t, "__args__") and len(_t.__args__) == 1
        return _t.__args__[0]

    inspection = FactoryInspection(some_nested_fwd_ref_annotation)
    type_ = _ensure_list_and_get_arg(inspection.args_annotations["d"])
    type_ = _ensure_list_and_get_arg(type_)
    assert type_ == SomeClass

    type_ = inspection.return_type
    assert type_
    type_ = _ensure_list_and_get_arg(type_)
    assert type_ == SomeClass


T = TypeVar("T")


class _G(Generic[T]):
    def __init__(self, x: str):
        self.x = x


class _X(_G[int]):
    pass


def test_generics():
    inspection = FactoryInspection(_X)
    assert inspection.args == ["x"]
    assert inspection.args_annotations == {"x": str}
    assert inspection.return_type == _X
