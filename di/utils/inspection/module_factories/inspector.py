import inspect
from typing import Callable, Collection, Tuple, Type

from di.utils.inspection.module_factories.base import (
    FactoryFilter,
    FactoryFilterCascade,
)


class ModuleFactoriesInspector:
    def __init__(self, filters: Collection[FactoryFilter]):
        self.filter_cascade = FactoryFilterCascade(filters)

    def filtered_factories(self, module):
        return [*self.filtered_types(module), *self.filtered_functions(module)]

    def filtered_types(self, module) -> Collection[Tuple[str, Type]]:
        items = self.all_types(module)
        return self.filter_cascade.apply(module, items)

    def filtered_functions(self, module) -> Collection[Tuple[str, Callable]]:
        items = self.all_functions(module)
        return self.filter_cascade.apply(module, items)

    def all_factories(self, module):
        return [*self.all_types(module), *self.all_functions(module)]

    @staticmethod
    def all_types(module) -> Collection[Tuple[str, Type]]:
        assert inspect.ismodule(module)
        return [
            (name, obj)
            for name, obj in module.__dict__.items()
            if isinstance(obj, type)
        ]

    @staticmethod
    def all_functions(module) -> Collection[Tuple[str, Callable]]:
        assert inspect.ismodule(module)
        return [
            (name, obj)
            for name, obj in module.__dict__.items()
            if inspect.isfunction(obj)
        ]
