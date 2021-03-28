import dis
import inspect
import re
from types import DynamicClassAttribute
from typing import Callable, Iterable, Set, Type

from di.utils.inspection.typing import BUILTIN_TYPES


class AbstractInspector:
    @classmethod
    def is_abstract(cls, obj, duck_typing: bool = True) -> bool:
        if inspect.isfunction(obj):
            if duck_typing:
                return cls.is_abstract_function(obj)
            else:
                return False
        elif inspect.isclass(obj):
            return cls.is_abstract_class(obj, duck_typing=duck_typing)
        else:
            return False

    @classmethod
    def is_abstract_function(cls, obj: Callable):
        if not inspect.isfunction(obj):
            raise TypeError(f"{obj!r} is not a function or method")
        return cls.is_abstract_routine(obj)

    @classmethod
    def is_abstract_class(cls, obj: Type, duck_typing: bool = True):
        if not inspect.isclass(obj):
            raise TypeError(f"{obj!r} is not a class")
        if inspect.isabstract(obj):
            return True
        elif not duck_typing:
            return False
        for name, fn in cls._all_class_fns(obj):
            if cls.is_abstract_routine(fn):
                return True
        return False

    @classmethod
    def is_abstract_routine(cls, obj: Callable):
        if not inspect.isroutine(obj):
            raise TypeError(f"{obj!r} is not a routine")
        result = cls._is_abstract_code_check(obj)
        if result is not None:
            return result
        return cls._is_abstract_hard_check(obj)

    @classmethod
    def _is_abstract_code_check(cls, obj):
        try:
            src = inspect.getsource(obj)
            return (
                re.search(r"^\s*raise\s+NotImplemented", src, flags=re.MULTILINE)
                is not None
            )
        except (OSError, TypeError):
            pass

    @classmethod
    def _is_abstract_hard_check(cls, obj):
        try:
            closure_vars = inspect.getclosurevars(obj)
            for value in closure_vars.builtins.values():
                if value is NotImplementedError or value is NotImplemented:
                    break
            else:
                return False
        except AttributeError:
            # can not determine - probably native or builtin code
            return False
        try:
            for instruction in dis.get_instructions(obj):
                if instruction.opname == "RAISE_VARARGS" and instruction.arg == 1:
                    return True
        except TypeError:
            pass
        return False

    @classmethod
    def _all_class_fns(cls, obj: Type):
        for name, obj in cls._all_class_members(obj):
            if inspect.isfunction(obj):
                yield name, obj
            elif isinstance(obj, (classmethod, staticmethod)):
                yield name, obj.__func__
            elif isinstance(obj, (property, DynamicClassAttribute)):
                if obj.fget:
                    yield f"{name}.fget", obj.fget
                if obj.fset:
                    yield f"{name}.fset", obj.fset
                if obj.fdel:
                    yield f"{name}.fdel", obj.fdel

    @classmethod
    def _all_class_members(cls, obj: Type):
        visited: Set[str] = set()
        for clazz in cls._all_concrete_bases(obj):
            for name, obj in clazz.__dict__.items():
                if name in visited:
                    continue
                visited.add(name)
                yield name, obj

    @classmethod
    def _all_concrete_bases(cls, obj: Type) -> Iterable[Type]:
        for clazz in obj.mro():
            if clazz in BUILTIN_TYPES:
                continue
            yield clazz
