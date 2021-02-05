import inspect
from typing import Any, Callable, Collection, Optional, Type, Union

from di.builder.filters import FactoryFilterSets, VariableFilterSets
from di.core.element import Element
from di.core.injectors import FactoryInjector, ValueInjector
from di.core.module.base import Module, ModuleRelated
from di.core.provide_strategies import LocalProvideStrategy, SingletonProvideStrategy
from di.utils.inspection.module.factories import FactoryFilter, ModuleFactoriesInspector
from di.utils.inspection.module.variables import (
    ModuleVariablesInspector,
    VariableFilter,
)


def _python_modules(python_modules: Union[Any, Collection[Any]]):
    if inspect.ismodule(python_modules):
        yield python_modules
        return
    for python_module in python_modules:
        assert inspect.ismodule(
            python_module
        ), f"Object {python_module} is not python module"
        yield python_module


class AppModuleBuilderEventHandler:
    def element_added(self, module: Module, element: Element):
        pass


class AppModuleBuilder(ModuleRelated):
    def __init__(
        self,
        module: Module,
        event_handlers: Optional[Collection[AppModuleBuilderEventHandler]] = None,
    ):
        self.module = module
        self.event_handlers = event_handlers or []

    def imports(
        self,
        *modules: Union[Module, "AppModuleBuilder"],
        reexport: Union[bool, Collection[Module]] = False,
    ):
        if reexport is True:
            reexport_modules = set(modules)
        elif not reexport:
            reexport_modules = ()
        else:
            reexport_modules = set(reexport)

        for module in modules:
            if isinstance(module, AppModuleBuilder):
                module = module.module
            self.module.imports.add(module)
            if module in reexport_modules:
                for element in module.exports:
                    self.module.exports.add(element)

    def scan_factories(
        self,
        python_modules: Union[Any, Collection[Any]],
        *filter_sets: Collection[FactoryFilter],
        non_singleton: bool = False,
        export: bool = True,
        bootstrap: bool = False,
    ):
        if not filter_sets:
            filter_sets = [FactoryFilterSets.domain()]
        elements = []
        for python_module in _python_modules(python_modules):
            for filter_set in filter_sets:
                inspector = ModuleFactoriesInspector(python_module, filter_set)
                elements.extend(
                    [
                        self.add_factory(
                            factory,
                            label=name,
                            non_singleton=non_singleton,
                            export=export,
                            bootstrap=bootstrap,
                        )
                        for name, factory in inspector.factories()
                    ]
                )
        return elements

    def add_factories(
        self,
        *factories: Union[Callable, Type],
        non_singleton: bool = False,
        export: bool = True,
        bootstrap: bool = False,
    ):
        return [
            self.add_factory(
                factory, non_singleton=non_singleton, export=export, bootstrap=bootstrap
            )
            for factory in factories
        ]

    def add_factory(
        self,
        factory: Union[Callable, Type],
        label: Optional[str] = None,
        *,
        non_singleton: bool = False,
        export: bool = True,
        bootstrap: bool = False,
    ):
        if non_singleton:
            strategy = LocalProvideStrategy()
        else:
            strategy = SingletonProvideStrategy()
        return self.add_element(
            element=Element(
                injector=FactoryInjector(factory),
                strategy=strategy,
                label=label,
            ),
            export=export,
            bootstrap=bootstrap,
        )

    def scan_values(
        self,
        python_modules: Union[Any, Collection[Any]],
        *filter_sets: Collection[VariableFilter],
        export: bool = True,
    ):
        if not filter_sets:
            filter_sets = [VariableFilterSets.domain()]
        elements = []
        for python_module in _python_modules(python_modules):
            for filter_set in filter_sets:
                inspector = ModuleVariablesInspector(python_module, filter_set)
                elements.extend(
                    [
                        self.add_value(var.value, label=var.name, export=export)
                        for var in inspector.variables()
                    ]
                )
        return elements

    def add_values(self, *values: Any, export: bool = True):
        return [self.add_value(value, export=export) for value in values]

    def add_value(
        self,
        value: Any,
        label: Optional[str] = None,
        *,
        export: bool = True,
    ):
        return self.add_element(
            element=Element(
                injector=ValueInjector(value),
                strategy=SingletonProvideStrategy(),
                label=label,
            ),
            export=export,
        )

    def add_element(
        self,
        element: Element,
        *,
        export: bool = True,
        bootstrap: bool = False,
    ):
        self.module.elements.add(element)
        if export:
            self.module.exports.add(element)
        if bootstrap:
            self.module.bootstrap.add(element)
        for event_handler in self.event_handlers:
            event_handler.element_added(self.module, element)
        return element
