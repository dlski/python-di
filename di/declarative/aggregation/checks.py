from typing import Callable

from di.core.element import Dependency
from di.utils.inspection import aggregated_type, is_compatible_type

IsAggregationType = Callable[[Dependency], bool]


def arg_check(arg_name: str) -> IsAggregationType:
    def _arg_check(d: Dependency):
        return d.arg == arg_name

    return _arg_check


def factory_arg_check(type_spec, arg_name: str) -> IsAggregationType:
    def _factory_arg_check(d: Dependency):
        return d.arg == arg_name and is_compatible_type(
            d.source.value().type, type_spec
        )

    return _factory_arg_check


def type_check(type_spec) -> IsAggregationType:
    def _type_check(d: Dependency):
        type_ = aggregated_type(d.type)
        if type_:
            return is_compatible_type(type_, type_spec)

    return _type_check
