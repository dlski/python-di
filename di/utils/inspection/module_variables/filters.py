from types import ModuleType
from typing import Iterable

from di.utils.inspection.module_variables.base import Variable, VariableFilter


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
            if var.is_set and var.value is not Ellipsis:
                yield var


class UndefinedVariableFilter(VariableFilter):
    def filter(
        self, module: ModuleType, variables: Iterable[Variable]
    ) -> Iterable[Variable]:
        for var in variables:
            if var.is_not_set or var.value is Ellipsis:
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
