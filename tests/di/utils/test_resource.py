from typing import Union

import pytest

from di.utils.resource import ModuleObjectKeyRef, ModuleObjectRef, ResourceNameError


class X:
    def __init__(self, x):
        self.x = x


def _assert_module_object_ref(ref: Union[ModuleObjectRef, ModuleObjectKeyRef]):
    assert ref.module == X.__module__
    assert ref.name == X.__name__
    assert ref.object == X


def test_module_object():
    ref = ModuleObjectRef.from_obj(X)
    _assert_module_object_ref(ref)

    ref = ModuleObjectRef.from_rn(f"{X.__module__}:{X.__name__}")
    _assert_module_object_ref(ref)

    with pytest.raises(ResourceNameError):
        ModuleObjectRef.from_rn("xyz")

    assert ModuleObjectRef.from_obj(X) == ModuleObjectRef.from_obj(X)
    ref_set = {ModuleObjectRef.from_obj(X), ModuleObjectRef.from_obj(X)}
    assert len(ref_set) == 1


def test_module_object_key():
    ref = ModuleObjectKeyRef.from_obj(X, "x")
    _assert_module_object_ref(ref)

    ref = ModuleObjectKeyRef.from_rn(f"{X.__module__}:{X.__name__}/x")
    _assert_module_object_ref(ref)
    assert ref.key == "x"

    with pytest.raises(ResourceNameError):
        ModuleObjectKeyRef.from_rn("xyz")

    with pytest.raises(ResourceNameError):
        ModuleObjectKeyRef.from_rn(f"{X.__module__}:{X.__name__}")

    assert ModuleObjectKeyRef.from_obj(X, "x") == ModuleObjectKeyRef.from_obj(X, "x")
    ref_set = {ModuleObjectKeyRef.from_obj(X, "x"), ModuleObjectKeyRef.from_obj(X, "x")}
    assert len(ref_set) == 1
