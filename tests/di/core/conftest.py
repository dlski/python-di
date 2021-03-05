from typing import Iterable, Sequence

import pytest

from di.core.app import Application
from di.core.element import Element
from di.core.injectors import FactoryInjector
from di.core.module import Module
from di.core.provide_strategies import SingletonProvideStrategy
from di.utils.compat import cached_property


class X:
    pass


class X2(X):
    pass


class Y:
    def __init__(self, x: X):
        self.x = x


class YAgg:
    def __init__(self, x: Iterable[X]):
        self.x = x


class Z:
    def __init__(self, x: X, y: Y, extra: str = "extra"):
        self.x = x
        self.y = y
        self.extra = extra


class XRec(X):
    def __init__(self, y: Y):
        self.y = y


def same_input_output(x: X) -> X:
    return x


_default_strategy = SingletonProvideStrategy()


def _create_elements(*factories) -> Sequence[Element]:
    return [
        Element(
            injector=FactoryInjector(c),
            strategy=_default_strategy,
        )
        for c in factories
    ]


@pytest.fixture
def unsatisfied_elements():
    return _create_elements(Z, Y)


@pytest.fixture
def simple_elements():
    return _create_elements(X, Y, Z)


@pytest.fixture
def redundant_elements():
    return _create_elements(X, X2, Y, Z)


@pytest.fixture
def cycle_elements():
    return _create_elements(XRec, Y)


@pytest.fixture
def same_input_output_elements():
    return _create_elements(same_input_output)


class A1:
    pass


class A2:
    def __init__(self, a1: A1):
        self.a1 = a1


class B1:
    def __init__(self, a2: A2):
        self.a2 = a2


class B2:
    def __init__(self, b1: B1, bc: "Bc"):
        self.b1 = b1
        self.bc = bc


class Bc:
    def __init__(self, b2: B2):
        self.b2 = b2


class C1:
    def __init__(self, a2: A2, b1: B1):
        self.a2 = a2
        self.b1 = b1


class C2:
    def __init__(self, c1: C1):
        self.c1 = c1


class AppGenerator:
    def __init__(self):
        self.a_elements = _create_elements(A1, A2)
        self.a_ma_elements = _create_elements(A2)
        self.b_elements = _create_elements(B1)
        self.b_cd_elements = _create_elements(B1, B2, Bc)
        self.c_elements = _create_elements(C1, C2)

    @cached_property
    def a_module(self):
        return Module(
            name="A",
            elements={*self.a_elements},
            exports={*self.a_elements},
        )

    @cached_property
    def b_module(self):
        return Module(
            name="B",
            imports={self.a_module},
            elements={*self.b_elements},
            exports={*self.b_elements},
        )

    @cached_property
    def c_module(self):
        return Module(
            name="C",
            imports={self.a_module, self.b_module},
            elements={*self.c_elements},
            exports={*self.c_elements},
        )

    @cached_property
    def a_ma_module(self):
        return Module(
            name="Ama",
            elements={*self.a_ma_elements},
            exports={*self.a_ma_elements},
        )

    @cached_property
    def b_ma_module(self):
        return Module(
            name="Bma",
            imports={self.a_ma_module},
            elements={*self.b_module.elements},
            exports={*self.b_module.exports},
        )

    @cached_property
    def b_cd_module(self):
        return Module(
            name="Bcd",
            imports={self.a_module},
            elements={*self.b_cd_elements},
            exports={*self.b_cd_elements},
        )

    @cached_property
    def a_b_ci_modules(self):
        a_ci = Module(
            name="Aci",
            elements={*self.a_module.elements},
            exports={*self.a_module.exports},
        )
        b_ci = Module(
            name="Bci",
            imports={a_ci},
            elements={*self.b_module.elements},
            exports={*self.b_module.exports},
        )
        a_ci.imports.add(b_ci)
        return a_ci, b_ci

    @cached_property
    def b_bs_module(self):
        return Module(
            name="Bbs",
            imports={self.a_module},
            elements={*self.b_elements},
            bootstrap={*self.b_elements},
            exports={*self.b_elements},
        )

    @cached_property
    def c_bs_module(self):
        return Module(
            name="Cbs",
            imports={self.a_module, self.b_bs_module},
            elements={*reversed(self.c_elements)},
            bootstrap={*reversed(self.c_elements)},
            exports={*self.c_module.exports},
        )

    @cached_property
    def inconsistent_module(self):
        return Module(
            name="Ic",
            elements={*self.a_module.elements},
            exports={*self.b_module.elements},
        )

    @cached_property
    def valid_app(self) -> Application:
        return Application(
            modules={self.c_module, self.b_module, self.a_module},
        )

    @cached_property
    def inconsistent_app(self):
        return Application(
            modules={self.inconsistent_module},
        )

    @cached_property
    def cyclic_import_app(self) -> Application:
        return Application(
            modules={*self.a_b_ci_modules},
        )

    @cached_property
    def missing_import_app(self) -> Application:
        return Application(
            modules={self.b_module},
        )

    @cached_property
    def missing_assignment_app(self) -> Application:
        return Application(
            modules={self.a_ma_module, self.b_ma_module},
        )

    @cached_property
    def cyclic_dependency_app(self) -> Application:
        return Application(
            modules={self.a_module, self.b_cd_module},
        )

    @cached_property
    def bootstrap_app(self) -> Application:
        return Application(
            modules={self.b_bs_module, self.a_module, self.c_bs_module},
        )


@pytest.fixture
def app_generator() -> AppGenerator:
    return AppGenerator()
