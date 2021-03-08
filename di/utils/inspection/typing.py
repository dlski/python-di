import itertools
from abc import ABCMeta
from collections import abc
from typing import (
    Any,
    FrozenSet,
    Iterable,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)


def _builtins_values():
    try:
        return __builtins__.values()
    except AttributeError:
        return __builtins__.__dict__.values()


_NoneType = type(None)
BUILTIN_TYPES = {
    type_
    for type_ in _builtins_values()
    if isinstance(type_, type) and not issubclass(type_, BaseException)
}

COLLECTION_ABC_TYPES = {
    type_
    for type_ in (getattr(abc, type_name) for type_name in dir(abc))
    if isinstance(type_, ABCMeta)
}

BASE_TYPES = {*BUILTIN_TYPES, *COLLECTION_ABC_TYPES}


def is_base_type(type_):
    for sub_type in _walk_types(type_):
        if sub_type not in BASE_TYPES:
            return False
    return True


def _walk_types(type_: Type[Any]) -> Iterable[Type[Any]]:
    type_ = _flatten_new_type(type_)
    origin = getattr(type_, "__origin__", None)
    if origin:
        yield origin
        for arg_type in getattr(type_, "__args__", ()):
            yield from _walk_types(arg_type)
    elif isinstance(type_, TypeVar):
        if type_.__bound__:
            yield type_.__bound__
    else:
        yield type_


def is_compatible_type(proposal: Optional, model: Optional) -> bool:
    if not proposal or not model:
        return False
    proposal = _flatten_new_type(proposal)
    model = _flatten_new_type(model)
    if isinstance(proposal, type) and isinstance(model, type):
        return issubclass(proposal, model)
    proposal_origin = getattr(proposal, "__origin__", None)
    model_origin = getattr(model, "__origin__", None)
    if proposal_origin is not Union and model_origin is Union:
        for model_arg in model.__args__:
            if is_compatible_type(proposal, model_arg):
                return True
        return False
    if proposal_origin is Union and model_origin is not Union:
        for proposal_arg in proposal.__args__:
            if not is_compatible_type(proposal_arg, model):
                return False
        return True
    if proposal_origin and model_origin:
        if proposal_origin is Union and model_origin is Union:
            for proposal_arg in proposal.__args__:
                for model_arg in model.__args__:
                    if is_compatible_type(proposal_arg, model_arg):
                        break
                else:
                    return False
            return True
        if not issubclass(proposal_origin, model_origin):
            return False
        for proposal_sub, model_sub in itertools.zip_longest(
            proposal.__args__, model.__args__
        ):
            if not is_compatible_type(proposal_sub, model_sub):
                return False
        return True
    return False


def aggregated_type(type_: Optional):
    types = tuple(_aggregated_types(type_))
    if not types:
        return None
    if len(types) == 1:
        return types[0]
    return Union[types]


def _aggregated_types(type_: Optional):
    for type_ in flatten_union(type_):
        origin = getattr(type_, "__origin__", None)
        if origin:
            if issubclass(origin, Iterable) and not issubclass(origin, Mapping):
                (arg_type,) = type_.__args__
                yield arg_type


def flatten_union(type_: Optional):
    if not type_:
        return
    type_ = _flatten_new_type(type_)
    origin = getattr(type_, "__origin__", None)
    if origin is Union:
        for arg_type in type_.__args__:
            yield from flatten_union(arg_type)
    else:
        yield type_


AGGREGATION_FACTORIES = [
    (Set, set),
    (FrozenSet, frozenset),
    (Tuple, tuple),
]


def aggregation_type_factory(type_):
    type_ = unwrap_optional(type_)
    origin = getattr(type_, "__origin__", None)
    assert origin
    for factory_origin, factory in AGGREGATION_FACTORIES:
        if issubclass(origin, factory_origin):
            return factory
    return list


def unwrap_optional(type_: Optional):
    if not type_:
        return
    type_ = _flatten_new_type(type_)
    origin = getattr(type_, "__origin__", None)
    if origin is Union:
        args = [arg for arg in type_.__args__ if arg is not _NoneType]
        if len(args) == 1:
            return unwrap_optional(args[0])
    return type_


def _flatten_new_type(type_):
    supertype = getattr(type_, "__supertype__", None)
    if supertype is not None:
        return _flatten_new_type(supertype)
    return type_
