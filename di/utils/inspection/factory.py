import inspect
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    get_type_hints,
)

from di.utils.compat import cached_property


class FactoryInspection:
    _kinds = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    )

    def __init__(self, _factory: Callable):
        self._factory = _factory
        self._factory_module = getattr(self._factory, "__module__", None)

        target = _factory.__init__ if isinstance(_factory, type) else _factory
        all_parameters: List[inspect.Parameter] = [
            *inspect.signature(target).parameters.values()
        ]
        skip_parameters = 1 if self._factory != target else 0
        self._parameters: List[inspect.Parameter] = all_parameters[skip_parameters:]
        self._annotations = get_type_hints(target)

    @cached_property
    def optional_args(self) -> Collection[str]:
        return {
            param.name
            for param in self._parameters
            if param.default is not inspect.Parameter.empty
        }

    @cached_property
    def args(self) -> Sequence[str]:
        return [param.name for param in self._parameters if param.kind in self._kinds]

    @cached_property
    def args_annotations(self):
        return {
            key: value_type
            for key, value_type in self._annotations.items()
            if key != "return"
        }

    @cached_property
    def return_type(self) -> Optional[Type[Any]]:
        if isinstance(self._factory, type):
            return self._factory
        return self._annotations.get("return")

    @cached_property
    def annotations(self) -> Dict[str, Type[Any]]:
        return self._annotations
