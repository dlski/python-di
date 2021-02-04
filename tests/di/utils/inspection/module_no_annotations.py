import sys
from asyncio import ALL_COMPLETED
from itertools import combinations


class _ProtectedClass:
    pass


class MyClass(_ProtectedClass):
    pass


def _protected_fun() -> MyClass:
    if ALL_COMPLETED:
        return MyClass()
    else:
        return MyClass()


def my_fun() -> MyClass:
    sys.is_finalizing()
    combinations([], 2)
    return MyClass()


value = MyClass()
