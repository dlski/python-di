import inspect
from functools import cached_property
from typing import Any, Callable, Collection, Dict, Optional, Sequence, Set, Type

from di.utils.inspection.typing import resolve_annotations


class FactoryInspection:
    def __init__(self, _factory: Callable):
        self._factory = _factory
        self._factory_module = getattr(self._factory, "__module__", None)
        self._arg_spec = inspect.getfullargspec(_factory)

    @cached_property
    def optional_args(self) -> Collection[str]:
        optional_args: Set[str] = set()
        if self._arg_spec.defaults:
            defaults_count = len(self._arg_spec.defaults)
            optional_args.update(
                self._arg_spec.args[-defaults_count:],
            )
        if self._arg_spec.kwonlydefaults:
            optional_args.update(self._arg_spec.kwonlydefaults)
        return optional_args

    @cached_property
    def args(self) -> Sequence[str]:
        if isinstance(self._factory, type):
            arg_offset = 1
        else:
            arg_offset = 0
        return self._arg_spec.args[arg_offset:] + self._arg_spec.kwonlyargs

    @cached_property
    def args_annotations(self):
        return {
            key: value_type
            for key, value_type in self.annotations.items()
            if key != "return"
        }

    @cached_property
    def return_type(self) -> Optional[Type[Any]]:
        if isinstance(self._factory, type):
            return self._factory
        return self.annotations.get("return")

    @cached_property
    def annotations(self) -> Dict[str, Type[Any]]:
        return resolve_annotations(self._arg_spec.annotations, self._factory_module)
