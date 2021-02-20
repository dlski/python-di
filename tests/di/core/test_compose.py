import itertools
from typing import Mapping

import pytest

from di.core.compose import (
    ApplicationComposer,
    ApplicationComposerConsistencyError,
    ApplicationComposerModuleAssignmentError,
    ApplicationComposerModuleCyclicDependencyError,
    ApplicationComposerUnresolvedImportError,
)
from di.core.injection import InjectionPlan, InjectionSolver
from di.core.module import Module, ModuleElementConsistencyCheck, ModuleImportSolver
from tests.di.core.conftest import AppGenerator


@pytest.fixture
def composer() -> ApplicationComposer:
    return ApplicationComposer(
        InjectionSolver(),
        ModuleImportSolver(),
        ModuleElementConsistencyCheck(),
    )


def test_compose_valid(app_generator: AppGenerator, composer: ApplicationComposer):
    gen = app_generator
    app = composer.compose(app_generator.valid_app)
    modules = [gen.a_module, gen.b_module, gen.c_module]
    for module_index, module in enumerate(modules):
        assert module in app.import_plan.steps[module_index]
        assert module == app.injection_plans[module_index].module

    module_plan_map: Mapping[Module, InjectionPlan] = {
        plan.module: plan for plan in app.injection_plans
    }
    for module in modules:
        assert module in module_plan_map
    for module in [gen.a_module, gen.b_module, gen.c_module]:
        plan = module_plan_map[module]
        plan_elements = {*itertools.chain(*plan.stages)}
        for element in module.elements:
            assert element in plan_elements


def test_compose_inconsistent(
    app_generator: AppGenerator, composer: ApplicationComposer
):
    with pytest.raises(ApplicationComposerConsistencyError):
        composer.compose(app_generator.inconsistent_app)


def test_compose_unresolved_import(
    app_generator: AppGenerator, composer: ApplicationComposer
):
    with pytest.raises(ApplicationComposerUnresolvedImportError):
        composer.compose(app_generator.cyclic_import_app)
    with pytest.raises(ApplicationComposerUnresolvedImportError):
        composer.compose(app_generator.missing_import_app)


def test_compose_missing_assignment(
    app_generator: AppGenerator, composer: ApplicationComposer
):
    try:
        composer.compose(app_generator.missing_assignment_app)
        pytest.fail("Exception not thrown")
    except ApplicationComposerModuleAssignmentError as error:
        assert error.module is app_generator.a_ma_module
        assert error.dependency.arg == "a1"
        assert error.dependency.type
        assert error.dependency.type.__name__ == "A1"


def test_cyclic_dependency(app_generator: AppGenerator, composer: ApplicationComposer):
    try:
        composer.compose(app_generator.cyclic_dependency_app)
    except ApplicationComposerModuleCyclicDependencyError as error:
        assert error.module == app_generator.b_cd_module


def test_bootstrap_sequence(app_generator: AppGenerator, composer: ApplicationComposer):
    app = composer.compose(app_generator.bootstrap_app)
    expected_sequence = [*app_generator.b_elements, *app_generator.c_elements]
    examined_sequence = []
    for module_step in app.bootstrap_steps:
        for step in module_step.steps:
            examined_sequence.extend(step)
    assert expected_sequence == examined_sequence
