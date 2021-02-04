from typing import Collection

from di.utils.inspection.module.variables import (
    AnnotatedVariableFilter,
    DefinedVariableFilter,
    ModuleVariablesInspector,
    OptionalAllVariableFilter,
    PublicVariableFilter,
    UndefinedVariableFilter,
    Variable,
)
from tests.di.utils.inspection import (
    module_all_present,
    module_empty_annotations,
    module_no_annotations,
)


def _names(variables: Collection[Variable]):
    return {var.name for var in variables if not var.name.startswith("__")}


def test_module_variables_all():
    inspector = ModuleVariablesInspector(module_all_present, [])
    assert {
        "variable",
        "variable_with_value",
    } == _names(inspector.all_variables())
    inspector = ModuleVariablesInspector(module_empty_annotations, [])
    assert {
        "variable",
        "_protected_variable",
        "variable_with_value",
        "_protected_variable_with_value",
        "ALL_COMPLETED",
    } == _names(inspector.all_variables())
    inspector = ModuleVariablesInspector(module_no_annotations, [])
    assert {
        "value",
        "ALL_COMPLETED",
    } == _names(inspector.all_variables())


def test_module_variables_annotated_filter():
    inspector = ModuleVariablesInspector(
        module_all_present, [AnnotatedVariableFilter()]
    )
    assert {
        "variable",
        "variable_with_value",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_empty_annotations, [AnnotatedVariableFilter()]
    )
    assert {
        "variable",
        "_protected_variable",
        "variable_with_value",
        "_protected_variable_with_value",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_no_annotations, [AnnotatedVariableFilter()]
    )
    assert not _names(inspector.variables())


def test_module_variables_defined_filter():
    inspector = ModuleVariablesInspector(module_all_present, [DefinedVariableFilter()])
    assert {
        "variable_with_value",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_empty_annotations, [DefinedVariableFilter()]
    )
    assert {
        "ALL_COMPLETED",
        "variable_with_value",
        "_protected_variable_with_value",
    } == _names(inspector.variables())


def test_module_variables_undefined_filter():
    inspector = ModuleVariablesInspector(
        module_all_present, [UndefinedVariableFilter()]
    )
    assert {
        "variable",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_empty_annotations, [UndefinedVariableFilter()]
    )
    assert {
        "variable",
        "_protected_variable",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_no_annotations, [AnnotatedVariableFilter()]
    )
    assert not _names(inspector.variables())


def test_module_variables_optional_all_filter():
    inspector = ModuleVariablesInspector(
        module_all_present, [OptionalAllVariableFilter()]
    )
    assert {
        "variable",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_empty_annotations, [OptionalAllVariableFilter()]
    )
    assert {
        "variable",
        "_protected_variable",
        "variable_with_value",
        "_protected_variable_with_value",
        "ALL_COMPLETED",
    } == _names(inspector.variables())


def test_module_variables_public_all_filter():
    inspector = ModuleVariablesInspector(module_all_present, [PublicVariableFilter()])
    assert {
        "variable",
        "variable_with_value",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_empty_annotations, [PublicVariableFilter()]
    )
    assert {
        "variable",
        "variable_with_value",
        "ALL_COMPLETED",
    } == _names(inspector.variables())
    inspector = ModuleVariablesInspector(
        module_no_annotations, [PublicVariableFilter()]
    )
    assert {
        "value",
        "ALL_COMPLETED",
    } == _names(inspector.variables())
