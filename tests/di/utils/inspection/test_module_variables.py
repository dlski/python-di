from typing import Collection

from di.utils.inspection.module_variables import (
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
    inspector = ModuleVariablesInspector([])
    assert {
        "variable",
        "variable_with_value",
    } == _names(inspector.all_variables(module_all_present))
    assert {
        "variable",
        "_protected_variable",
        "variable_with_value",
        "_protected_variable_with_value",
        "ALL_COMPLETED",
    } == _names(inspector.all_variables(module_empty_annotations))
    assert {
        "value",
        "ALL_COMPLETED",
    } == _names(inspector.all_variables(module_no_annotations))


def test_module_variables_annotated_filter():
    inspector = ModuleVariablesInspector([AnnotatedVariableFilter()])
    assert {
        "variable",
        "variable_with_value",
    } == _names(inspector.variables(module_all_present))
    assert {
        "variable",
        "_protected_variable",
        "variable_with_value",
        "_protected_variable_with_value",
    } == _names(inspector.variables(module_empty_annotations))
    assert not _names(inspector.variables(module_no_annotations))


def test_module_variables_defined_filter():
    inspector = ModuleVariablesInspector([DefinedVariableFilter()])
    assert {
        "variable_with_value",
    } == _names(inspector.variables(module_all_present))
    assert {
        "ALL_COMPLETED",
        "variable_with_value",
        "_protected_variable_with_value",
    } == _names(inspector.variables(module_empty_annotations))


def test_module_variables_undefined_filter():
    inspector = ModuleVariablesInspector([UndefinedVariableFilter()])
    assert {
        "variable",
    } == _names(inspector.variables(module_all_present))
    assert {
        "variable",
        "_protected_variable",
    } == _names(inspector.variables(module_empty_annotations))
    assert not _names(inspector.variables(module_no_annotations))


def test_module_variables_optional_all_filter():
    inspector = ModuleVariablesInspector([OptionalAllVariableFilter()])
    assert {
        "variable",
    } == _names(inspector.variables(module_all_present))
    assert {
        "variable",
        "_protected_variable",
        "variable_with_value",
        "_protected_variable_with_value",
        "ALL_COMPLETED",
    } == _names(inspector.variables(module_empty_annotations))


def test_module_variables_public_all_filter():
    inspector = ModuleVariablesInspector([PublicVariableFilter()])
    assert {
        "variable",
        "variable_with_value",
    } == _names(inspector.variables(module_all_present))
    assert {
        "variable",
        "variable_with_value",
        "ALL_COMPLETED",
    } == _names(inspector.variables(module_empty_annotations))
    assert {
        "value",
        "ALL_COMPLETED",
    } == _names(inspector.variables(module_no_annotations))
