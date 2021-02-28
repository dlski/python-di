import dataclasses
from types import ModuleType
from typing import Collection, Iterable, Type, Union

from di.utils.inspection.abstract import AbstractInspector
from di.utils.inspection.module_factories.base import FactoryFilter, FactoryItem


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
