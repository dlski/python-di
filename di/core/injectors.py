from typing import Callable, Iterable, Optional, Type

from di.core.element import InjectionResult, Injector, InjectorDependency
from di.utils.inspection import FactoryInspection
from di.utils.resource import ModuleObjectRef


class FactoryInjector(Injector):
    def __init__(
        self,
        factory: Callable,
        force_type: Optional[Type] = None,
        ref: Optional[ModuleObjectRef] = None,
    ):
        self._factory = factory
        self._ref = ref or ModuleObjectRef.from_obj(factory)
        inspection = FactoryInspection(factory)
        self._args = inspection.args
        self._optional_args = inspection.optional_args
        self._args_annotations = inspection.args_annotations
        self._return_type = force_type or inspection.return_type

    def dependencies(self) -> Iterable[InjectorDependency]:
        return [
            InjectorDependency(
                arg=arg,
                type=self._args_annotations.get(arg),
                mandatory=arg not in self._optional_args,
            )
            for arg in self._args
        ]

    @property
    def ref(self) -> Optional[ModuleObjectRef]:
        return self._ref

    def result(self) -> Optional[InjectionResult]:
        return InjectionResult(type=self._return_type)

    def __call__(self, *args, **kwargs):
        return self._factory(*args, **kwargs)


class ValueInjector(Injector):
    def __init__(self, value, ref: Optional[ModuleObjectRef] = None):
        self._value = value
        self._value_type = type(value) if value is not None else None
        self._ref = ref

    @property
    def ref(self) -> Optional[ModuleObjectRef]:
        if not isinstance(self._value, type):
            return ModuleObjectRef.from_obj(self._value_type)

    def result(self) -> Optional[InjectionResult]:
        return InjectionResult(type=self._value_type)

    def __call__(self, *args, **kwargs):
        return self._value
