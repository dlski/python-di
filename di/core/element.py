from dataclasses import dataclass
from typing import Any, Iterable, MutableMapping, Optional, Type


@dataclass
class InjectorDependency:
    arg: str
    type: Optional[Type] = None
    mandatory: bool = True


@dataclass
class InjectionResult:
    type: Optional[Type] = None


class Injector:
    def dependencies(self) -> Iterable[InjectorDependency]:
        return ()

    def result(self) -> Optional[InjectionResult]:
        return None

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


@dataclass
class ElementSourced:
    source: "Element"


@dataclass
class Value(InjectionResult, ElementSourced):
    def __hash__(self):
        return hash(self.source)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.source == other.source
        return False


@dataclass
class Dependency(InjectorDependency, ElementSourced):
    def __hash__(self):
        return hash((self.source, self.arg))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.source == other.source and self.arg == other.arg


@dataclass
class Element:
    injector: Injector
    strategy: "ProvideStrategy"
    label: Optional[str] = None

    def dependencies(self) -> Iterable[Dependency]:
        return tuple(
            Dependency(
                source=self,
                arg=dep.arg,
                type=dep.type,
                mandatory=dep.mandatory,
            )
            for dep in self.injector.dependencies()
        )

    def value(self) -> Value:
        result = self.injector.result()
        return Value(
            source=self,
            type=result and result.type,
        )

    __hash__ = object.__hash__
    __eq__ = object.__eq__


class ProvideContext:
    global_state: MutableMapping[Element, Any]

    def eval(self, element: Element):
        raise NotImplementedError


class ProvideStrategy:
    def provide(self, context: ProvideContext, element: Element) -> Any:
        raise NotImplementedError


__all__ = [
    "InjectorDependency",
    "InjectionResult",
    "Injector",
    "ElementSourced",
    "Value",
    "Dependency",
    "Element",
    "ProvideContext",
    "ProvideStrategy",
]
