import pytest

from di.core.compose.base import ComposedApplication
from di.core.compose.composers import ApplicationComposer
from di.core.element import Element
from di.core.injection.solvers import InjectionSolver
from di.core.instance.base import ApplicationInstanceElementNotFound
from di.core.instance.recurrent import (
    RecurrentApplicationInstance,
    RecurrentApplicationInstanceBuilder,
    RecurrentProvideContext,
)
from di.core.module.solvers import ModuleElementConsistencyCheck, ModuleImportSolver
from tests.di.core.conftest import AppGenerator


@pytest.fixture
def composer():
    return ApplicationComposer(
        InjectionSolver(),
        ModuleImportSolver(),
        ModuleElementConsistencyCheck(),
    )


@pytest.fixture
def composed(
    app_generator: AppGenerator, composer: ApplicationComposer
) -> ComposedApplication:
    return composer.compose(app_generator.valid_app)


def _build_instance(composed: ComposedApplication) -> RecurrentApplicationInstance:
    return RecurrentApplicationInstanceBuilder(composed).build()


def test_instance(composed: ComposedApplication, app_generator: AppGenerator):
    gen = app_generator
    instance = _build_instance(composed)

    a1e, a2e = gen.a_elements
    (b1e,) = gen.b_elements
    c1e, c2e = gen.c_elements
    c2 = instance.value_of(c2e)
    c1 = instance.value_of(c1e)
    b1 = instance.value_of(b1e)
    a2 = instance.value_of(a2e)
    a1 = instance.value_of(a1e)
    assert c2.c1 is c1
    assert c1.a2 is a2
    assert c1.b1 is b1
    assert a2.a1 is a1


def test_instance_not_found(composed: ComposedApplication, app_generator: AppGenerator):
    gen = app_generator
    instance = _build_instance(composed)

    bce = gen.b_cd_elements[-1]
    with pytest.raises(ApplicationInstanceElementNotFound):
        instance.value_of(bce)


class _RecurrentProvideContext(RecurrentProvideContext):
    _call_stack = []
    primary_sequence = []

    def provide(self, element: Element):
        if not self._call_stack:
            self.primary_sequence.append(element)
        self._call_stack.append(self)
        try:
            super().provide(element)
        finally:
            self._call_stack.pop()


class _RecurrentApplicationInstanceBuilder(RecurrentApplicationInstanceBuilder):
    def _provide_context(self):
        return _RecurrentProvideContext(self.app)


def test_instance_bootstrap(app_generator: AppGenerator, composer: ApplicationComposer):
    composed = composer.compose(app_generator.bootstrap_app)
    _RecurrentApplicationInstanceBuilder(composed).build()
    expected_sequence = []
    for module_step in composed.bootstrap_steps:
        for step in module_step.steps:
            expected_sequence.extend(step)
    produced_sequence = _RecurrentProvideContext.primary_sequence
    assert expected_sequence == produced_sequence
