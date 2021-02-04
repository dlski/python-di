from typing import Collection

from di.utils.inspection.module.factories import (
    AllFactoryFilter,
    FactoryItem,
    InternalsFactoryFilter,
    InternalsOrAllFactoryFilter,
    ModuleFactoriesInspector,
    NonAbstractFactoryFilter,
    NonDataclassFactoryFilter,
    NonTypeFactoryFilter,
    PublicFactoryFilter,
)
from tests.di.utils.inspection import (
    module_abstract,
    module_all_present,
    module_empty_annotations,
    module_model,
)


def _names(factories: Collection[FactoryItem]):
    return {name for name, _ in factories}


def test_module_factories_all_classes():
    inspector = ModuleFactoriesInspector(module_empty_annotations, [])
    assert {
        "ABC",
        "combinations",
        "_ProtectedClass",
        "MyClass",
    } == _names(inspector.all_classes())


def test_modules_all_functions():
    inspector = ModuleFactoriesInspector(module_empty_annotations, [])
    assert {
        "abstractmethod",
        "gather",
        "_protected_fun",
        "my_fun",
    } == _names(inspector.all_functions())


def test_module_factories_all_factory_filter():
    inspector = ModuleFactoriesInspector(module_all_present, [AllFactoryFilter()])
    assert {
        "OtherClass",
        "my_fun2",
    } == _names(inspector.factories())


def test_module_internals_factories_filter():
    inspector = ModuleFactoriesInspector(
        module_empty_annotations, [InternalsFactoryFilter()]
    )
    assert {
        "_ProtectedClass",
        "MyClass",
        "_protected_fun",
        "my_fun",
    } == _names(inspector.factories())


def test_module_internals_or_all_filter():
    inspector = ModuleFactoriesInspector(
        module_all_present, [InternalsOrAllFactoryFilter()]
    )
    assert {
        "OtherClass",
        "my_fun2",
    } == _names(inspector.factories())
    inspector = ModuleFactoriesInspector(
        module_empty_annotations, [InternalsOrAllFactoryFilter()]
    )
    assert {
        "_ProtectedClass",
        "MyClass",
        "_protected_fun",
        "my_fun",
    } == _names(inspector.factories())


def test_module_public_filter():
    inspector = ModuleFactoriesInspector(
        module_empty_annotations, [PublicFactoryFilter()]
    )
    assert {
        "ABC",
        "abstractmethod",
        "combinations",
        "gather",
        "MyClass",
        "my_fun",
    } == _names(inspector.factories())


def test_module_non_abstract_filter():
    inspector = ModuleFactoriesInspector(
        module_empty_annotations, [NonAbstractFactoryFilter()]
    )
    assert {
        "ABC",
        "abstractmethod",
        "combinations",
        "gather",
        "MyClass",
        "_protected_fun",
        "my_fun",
    } == _names(inspector.factories())


def test_module_non_abstract_canonical_filter():
    inspector = ModuleFactoriesInspector(
        module_abstract, [NonAbstractFactoryFilter(duck_typing=False)]
    )
    assert {
        "ABC",
        "abstractmethod",
        "NormalClass",
        "DuckAbstract1",
        "DuckAbstract2",
        "DuckAbstract3",
        "DuckAbstract4",
        "DuckAbstract5",
        "ImplementedAbstracts",
        "normal_fn",
        "abstract_fn",
        "normal_async_fn",
        "abstract_async_fn",
    } == _names(inspector.factories())


def test_module_non_abstract_duck_filter():
    inspector = ModuleFactoriesInspector(
        module_abstract, [NonAbstractFactoryFilter(duck_typing=True)]
    )
    assert {
        "ABC",
        "abstractmethod",
        "NormalClass",
        "ImplementedAbstracts",
        "normal_fn",
        "normal_async_fn",
    } == _names(inspector.factories())


def test_module_non_dataclass_filter():
    inspector = ModuleFactoriesInspector(module_model, [NonDataclassFactoryFilter()])
    assert {
        "dataclass",
        "NormalClass",
        "ExtendedNormalClass",
    } == _names(inspector.factories())


def test_module_non_model_filter():
    inspector = ModuleFactoriesInspector(
        module_model, [NonTypeFactoryFilter(types=module_model.NormalClass)]
    )
    assert {
        "dataclass",
        "DataClass",
    } == _names(inspector.factories())
