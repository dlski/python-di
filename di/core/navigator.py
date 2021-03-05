from collections import defaultdict
from typing import (
    Callable,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from di.core.app import Application, ApplicationRelated
from di.core.element import Element
from di.core.module.base import Module, ModuleRelated
from di.utils.compat import cached_property
from di.utils.inspection import is_base_type


class _NavigatorNameModuleMap:
    def __init__(self, modules: Collection[Module]):
        self._name_map = self._make_name_map(modules)

    def lookup(self, name: str) -> Module:
        modules = self._name_map.get(name)
        if not modules:
            raise LookupError(f"Module {name!r} not found")
        elif len(modules) > 1:
            raise LookupError(f"More than one module is named {name!r}")
        return modules[0]

    @classmethod
    def _make_name_map(cls, modules: Collection[Module]):
        name_map: Dict[str, List[Module]] = defaultdict(list)
        for module in modules:
            if module.name:
                name_map[module.name].append(module)
        return name_map


class _NavigatorTypeElementMap:
    def __init__(self, elements: Collection[Element], strict: bool = True):
        self._type_map = self._make_type_map(
            self._iterate_type if strict else self._iterate_subtypes, elements
        )

    def lookup(self, type_: Type) -> Collection[Element]:
        if type_ in self._type_map:
            return self._type_map[type_]
        else:
            raise LookupError(f"Element compatible with {type_} not found")

    def extend(self, other: "_NavigatorTypeElementMap"):
        mine_map = self._type_map
        for other_key, other_elements in other._type_map.items():
            mine_map[other_key].extend(other_elements)

    @classmethod
    def _make_type_map(
        cls,
        iterator: Callable[[Element], Iterable[Type]],
        elements: Collection[Element],
    ):
        type_map: Dict[Type, List[Element]] = defaultdict(list)
        for element in elements:
            for sub_type in iterator(element):
                type_map[sub_type].append(element)
        return type_map

    @classmethod
    def _iterate_type(cls, element: Element):
        type_ = element.value().type
        if type_:
            yield type_

    @classmethod
    def _iterate_subtypes(cls, element: Element):
        type_ = element.value().type
        if type_:
            yield from (
                sub_type for sub_type in type_.mro() if not is_base_type(sub_type)
            )

    @classmethod
    def join(
        cls, *ingredients: "_NavigatorTypeElementMap"
    ) -> "_NavigatorTypeElementMap":
        map_ = _NavigatorTypeElementMap([])
        for ingredient in ingredients:
            map_.extend(ingredient)
        return map_


class ApplicationNavigator(ApplicationRelated):
    def __init__(self, app: Application):
        self.app = app
        self._type_maps: Dict[Tuple, _NavigatorTypeElementMap] = {}

    def by_type(
        self,
        type_: Type,
        module: Optional[Union[Module, ModuleRelated, str]] = None,
        strict: bool = True,
    ) -> Collection[Element]:
        if module:
            module = self.get_module(module)
        type_map = self._get_type_map(module=module, strict=strict)
        return type_map.lookup(type_)

    def get_module(self, module: Union[str, Module, ModuleRelated]) -> Module:
        if isinstance(module, str):
            return self._name_module_map.lookup(module)
        elif isinstance(module, Module):
            return module
        elif isinstance(module, ModuleRelated):
            return module.module
        raise TypeError(f"Module argument type {type(module)} is not supported")

    @cached_property
    def _name_module_map(self) -> _NavigatorNameModuleMap:
        return _NavigatorNameModuleMap(self.app.modules)

    def _get_type_map(self, module: Optional[Module], strict: bool):
        key = module, strict
        if key in self._type_maps:
            map_ = self._type_maps[key]
        else:
            self._type_maps[key] = map_ = _NavigatorTypeElementMap(
                elements=module.elements if module else self.app.elements,
                strict=strict,
            )
        return map_
