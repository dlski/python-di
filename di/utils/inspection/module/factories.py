import dataclasses
import inspect
from types import ModuleType
from typing import Any, Callable, Collection, Iterable, Tuple, Type, Union

from di.utils.inspection.abstract import AbstractInspector

FactoryItem = Tuple[str, Any]


class FactoryFilter:
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        raise NotImplementedError


class AllFactoryFilter(FactoryFilter):
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        all_exported = {*getattr(module, "__all__", [])}
        for name, obj in items:
            if name in all_exported:
                yield name, obj


class InternalsFactoryFilter(FactoryFilter):
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        module_name = module.__name__
        for name, obj in items:
            if obj.__module__ == module_name:
                yield name, obj


class InternalsOrAllFactoryFilter(FactoryFilter):
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        if hasattr(module, "__all__"):
            factory_filter = AllFactoryFilter()
        else:
            factory_filter = InternalsFactoryFilter()
        yield from factory_filter.filter(module, items)


class PublicFactoryFilter(FactoryFilter):
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        for name, obj in items:
            if not name.startswith("_"):
                yield name, obj


class NonAbstractFactoryFilter(FactoryFilter):
    def __init__(self, duck_typing: bool = True):
        self.duck_typing = duck_typing

    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        for name, obj in items:
            if not AbstractInspector.is_abstract(obj, duck_typing=self.duck_typing):
                yield name, obj


class NonDataclassFactoryFilter(FactoryFilter):
    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        for name, obj in items:
            if dataclasses.is_dataclass(obj):
                continue
            yield name, obj


class NonTypeFactoryFilter(FactoryFilter):
    def __init__(self, types: Union[Type, Collection[Type]]):
        if not isinstance(types, type):
            types = tuple(types)
        self.types = types

    def filter(
        self, module: ModuleType, items: Iterable[FactoryItem]
    ) -> Iterable[FactoryItem]:
        for name, obj in items:
            if isinstance(obj, type) and issubclass(obj, self.types):
                continue
            yield name, obj


class FactoryFilterCascade:
    def __init__(self, filters: Collection[FactoryFilter]):
        self.filters = filters

    def apply(self, module: ModuleType, items: Iterable[FactoryItem]):
        for filter_ in self.filters:
            items = [*filter_.filter(module, items)]
        return items


class ModuleFactoriesInspector:
    def __init__(self, module, filters: Collection[FactoryFilter]):
        assert inspect.ismodule(module)
        self.module = module
        self.filter_cascade = FactoryFilterCascade(filters)

    def all_factories(self):
        return [*self.all_classes(), *self.all_functions()]

    def factories(self):
        return [*self.classes(), *self.functions()]

    def functions(self) -> Collection[Tuple[str, Callable]]:
        items = self.all_functions()
        return self.filter_cascade.apply(self.module, items)

    def all_functions(self) -> Collection[Tuple[str, Callable]]:
        return [
            (name, obj)
            for name, obj in self.module.__dict__.items()
            if inspect.isfunction(obj)
        ]

    def classes(self) -> Collection[Tuple[str, Type]]:
        items = self.all_classes()
        return self.filter_cascade.apply(self.module, items)

    def all_classes(self) -> Collection[Tuple[str, Type]]:
        return [
            (name, obj)
            for name, obj in self.module.__dict__.items()
            if isinstance(obj, type)
        ]
