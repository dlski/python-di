class _ProtectedClass:
    pass


class MyClass:
    pass


class OtherClass(MyClass):
    pass


def _protected_fun() -> MyClass:
    return variable  # noqa: F821


def my_fun() -> MyClass:
    return variable  # noqa: F821


def my_fun2() -> MyClass:
    return variable  # noqa: F821


variable: MyClass
variable_with_value: MyClass = MyClass()


__all__ = [  # noqa: F822
    "OtherClass",
    "my_fun2",
    "variable",
]
