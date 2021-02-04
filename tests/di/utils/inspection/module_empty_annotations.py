import sys
from abc import ABC, abstractmethod
from asyncio import ALL_COMPLETED, gather
from itertools import combinations
from typing import Optional


class _ProtectedClass(ABC):
    @abstractmethod
    def test(self):
        pass


class MyClass(_ProtectedClass):
    def test(self):
        return None


def _protected_fun() -> MyClass:
    if ALL_COMPLETED:
        return variable
    else:
        return MyClass()


def my_fun() -> MyClass:
    assert gather
    sys.is_finalizing()
    combinations([], 2)
    return variable


variable: MyClass = ...
_protected_variable: MyClass

variable_with_value: MyClass = MyClass()
_protected_variable_with_value: Optional[MyClass] = None
