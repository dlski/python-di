import inspect
from dataclasses import dataclass
from typing import Any, Callable, Collection, Iterator, Optional, Type, Union

from di.core.injectors import FactoryInjector, ValueInjector
from di.declarative.aggregation import IsAggregationType
from di.declarative.element.base import ModuleElement, ModuleElementIterable
from di.declarative.element.filters import FactoryFilterSets, VariableFilterSets
from di.utils.inspection.module_factories import FactoryFilter, ModuleFactoriesInspector
from di.utils.inspection.module_variables import (
    ModuleVariablesInspector,
    VariableFilter,
)


def _python_modules(python_modules: Collection[Any]) -> Iterator[Any]:
    for python_module in python_modules:
        if not inspect.ismodule(python_module):
            raise ValueError(f"Object {python_module} is not python module")
        yield python_module


def _factory_name(factory) -> Optional[str]:
    return getattr(factory, "__name__", None)


@dataclass
class _ScanFactories(ModuleElementIterable):
    python_modules: Collection[Any]
    filter_sets: Collection[Collection[FactoryFilter]]
    singleton: bool
    export: bool
    bootstrap: bool
    agg_checks: Collection[IsAggregationType]

    def __iter__(self) -> Iterator[ModuleElement]:
        for python_module in self.python_modules:
            for filters in self.filter_sets:
                inspector = ModuleFactoriesInspector(filters=filters)
                for name, factory in inspector.filtered_factories(python_module):
                    yield ModuleElement.create(
                        injector=FactoryInjector(factory),
                        singleton=self.singleton,
                        label=_factory_name(factory),
                        export=self.export,
                        bootstrap=self.bootstrap,
                        agg_checks=self.agg_checks,
                    )


def scan_factories(
    *python_modules: Any,
    filter_sets: Collection[Collection[FactoryFilter]] = (),
    singleton: bool = True,
    export: bool = True,
    bootstrap: bool = False,
    agg_checks: Collection[IsAggregationType] = (),
) -> ModuleElementIterable:
    return _ScanFactories(
        python_modules=[*_python_modules(python_modules)],
        filter_sets=filter_sets or (FactoryFilterSets.domain(),),
        singleton=singleton,
        export=export,
        bootstrap=bootstrap,
        agg_checks=agg_checks,
    )


@dataclass
class _AddFactories(ModuleElementIterable):
    factories: Collection[Union[Callable, Type]]
    singleton: bool
    export: bool
    bootstrap: bool
    agg_checks: Collection[IsAggregationType]

    def __iter__(self) -> Iterator[ModuleElement]:
        for factory in self.factories:
            yield ModuleElement.create(
                injector=FactoryInjector(factory),
                singleton=self.singleton,
                label=_factory_name(factory),
                export=self.export,
                bootstrap=self.bootstrap,
                agg_checks=self.agg_checks,
            )


def add_factories(
    *factories: Union[Callable, Type],
    singleton: bool = True,
    export: bool = True,
    bootstrap: bool = False,
    agg_checks: Collection[IsAggregationType] = (),
) -> ModuleElementIterable:
    return _AddFactories(
        factories=factories,
        singleton=singleton,
        export=export,
        bootstrap=bootstrap,
        agg_checks=agg_checks,
    )


@dataclass
class _ScanValues(ModuleElementIterable):
    python_modules: Union[Any, Collection[Any]]
    filter_sets: Collection[Collection[VariableFilter]]
    export: bool

    def __iter__(self) -> Iterator[ModuleElement]:
        for python_module in self.python_modules:
            for filters in self.filter_sets:
                inspector = ModuleVariablesInspector(filters)
                for var in inspector.variables(python_module):
                    yield ModuleElement.create(
                        injector=ValueInjector(var.value),
                        label=var.name,
                        export=self.export,
                    )


def scan_values(
    *python_modules: Any,
    filter_sets: Collection[Collection[VariableFilter]] = (),
    export: bool = True,
) -> ModuleElementIterable:
    return _ScanValues(
        python_modules=[*_python_modules(python_modules)],
        filter_sets=filter_sets or (VariableFilterSets.domain(),),
        export=export,
    )


@dataclass
class _AddValues(ModuleElementIterable):
    values: Collection[Any]
    export: bool

    def __iter__(self) -> Iterator[ModuleElement]:
        for value in self.values:
            yield ModuleElement.create(
                injector=ValueInjector(value),
                export=self.export,
            )


def add_values(*values: Any, export: bool = True) -> ModuleElementIterable:
    return _AddValues(
        values=values,
        export=export,
    )
