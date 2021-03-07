from di.declarative.aggregation.checks import (
    IsAggregationType,
    arg_check,
    factory_arg_check,
    type_check,
)
from di.declarative.aggregation.registry import AggRegistry
from di.declarative.aggregation.selector import AggAssigmentFactorySelector

__all__ = [
    # checks
    "IsAggregationType",
    "arg_check",
    "factory_arg_check",
    "type_check",
    # registry
    "AggRegistry",
    # selector
    "AggAssigmentFactorySelector",
]
