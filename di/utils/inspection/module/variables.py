import inspect
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Collection, Iterable, _GenericAlias, _SpecialForm

undefined = object()


@dataclass
class Variable:
    module: object
    name: str
    annotation: Any = None
    value: Any = undefined

    @property
    def is_set(self) -> bool:
        return self.value is not undefined


class VariableFilter:
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        raise NotImplementedError


class AnnotatedVariableFilter(VariableFilter):
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        for var in variables:
            if var.annotation:
                yield var


class DefinedVariableFilter(VariableFilter):
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        for var in variables:
            if var.value is not undefined and var.value is not Ellipsis:
                yield var


class UndefinedVariableFilter(VariableFilter):
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        for var in variables:
            if var.value is undefined or var.value is Ellipsis:
                yield var


class OptionalAllVariableFilter(VariableFilter):
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        all_ = getattr(module, "__all__", None)
        if all_ is None:
            yield from variables
            return
        for var in variables:
            if var.name in all_:
                yield var


class PublicVariableFilter(VariableFilter):
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        for var in variables:
            if not var.name.startswith("_"):
                yield var


class VariableFilterCascade:
    def __init__(self, filters: Collection[VariableFilter]):
        self.filters = filters

    def apply(self, module: ModuleType, variables: Iterable[Variable]):
        for filter_ in self.filters:
            variables = [*filter_.filter(module, variables)]
        return variables


class ModuleVariablesInspector:
    def __init__(self, module, filters: Collection[VariableFilter]):
        assert inspect.ismodule(module)
        self.module = module
        self.filter_cascade = VariableFilterCascade(filters)

    def variables(self):
        variables = self.all_variables()
        return self.filter_cascade.apply(self.module, variables)

    def all_variables(self):
        return [*self._all_variables()]

    def _all_variables(self):
        all_ = self.module.__dict__
        annotations = getattr(self.module, "__annotations__", {})
        for name, value in all_.items():
            if inspect.ismodule(value):
                continue
            if inspect.isfunction(value):
                continue
            if isinstance(value, (type, _GenericAlias, _SpecialForm)):
                continue
            yield Variable(
                module=self.module,
                name=name,
                annotation=annotations.get(name),
                value=value,
            )
        for name, annotation in annotations.items():
            if name in all_:
                continue
            yield Variable(
                module=self.module,
                name=name,
                annotation=annotations,
            )
