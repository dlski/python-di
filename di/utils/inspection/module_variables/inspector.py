import inspect
from typing import Collection, _GenericAlias, _SpecialForm, get_type_hints

from di.utils.inspection.module_variables.base import (
    Variable,
    VariableFilter,
    VariableFilterCascade,
)


class ModuleVariablesInspector:
    def __init__(self, filters: Collection[VariableFilter]):
        self.filter_cascade = VariableFilterCascade(filters)

    def variables(self, module):
        variables = self.all_variables(module)
        return self.filter_cascade.apply(module, variables)

    @classmethod
    def all_variables(cls, module):
        return [*cls._all_variables(module)]

    @staticmethod
    def _all_variables(module):
        assert inspect.ismodule(module)
        all_ = module.__dict__
        annotations = get_type_hints(module)
        for name, value in all_.items():
            if inspect.ismodule(value):
                continue
            if inspect.isfunction(value):
                continue
            if isinstance(value, (type, _GenericAlias, _SpecialForm)):
                continue
            yield Variable(
                module=module,
                name=name,
                annotation=annotations.get(name),
                value=value,
            )
        for name, annotation in annotations.items():
            if name in all_:
                continue
            yield Variable(
                module=module,
                name=name,
                annotation=annotations,
            )
