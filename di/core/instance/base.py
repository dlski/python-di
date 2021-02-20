from typing import Any, Iterable, Optional, Type, Union

from di.core.element import Element
from di.core.module import Module, ModuleRelated


class ApplicationInstanceStateError(AssertionError):
    pass


class ApplicationInstanceError(Exception):
    pass


class ApplicationInstanceElementNotFound(ApplicationInstanceError):
    def __init__(self, element: Element):
        super().__init__(f"Element {element} not found")
        self.element = element


class ApplicationInstance:
    def values_by_type(
        self,
        type_: Type,
        module: Optional[Union[Module, ModuleRelated, str]] = None,
        strict: bool = True,
    ) -> Iterable[Any]:
        raise NotImplementedError

    def value_of(self, element: Element):
        raise NotImplementedError


class ApplicationInstanceBuilder:
    def build(self) -> ApplicationInstance:
        raise NotImplementedError
