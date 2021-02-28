from dataclasses import dataclass
from types import ModuleType
from typing import Any, Collection, Iterable

_undefined = object()


@dataclass
class Variable:
    module: object
    name: str
    annotation: Any = None
    value: Any = _undefined

    @property
    def is_set(self) -> bool:
        return self.value is not _undefined

    @property
    def is_not_set(self) -> bool:
        return self.value is _undefined


class VariableFilter:
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        raise NotImplementedError


class VariableFilterCascade:
    def __init__(self, filters: Collection[VariableFilter]):
        self.filters = filters

    def apply(self, module: ModuleType, variables: Iterable[Variable]):
        for filter_ in self.filters:
            variables = [*filter_.filter(module, variables)]
        return variables
