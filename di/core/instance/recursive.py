from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Type, Union

from di.core.assignment import Assignment
from di.core.compose import ComposedApplication
from di.core.element import Element, ProvideContext
from di.core.instance.base import (
    ApplicationInstance,
    ApplicationInstanceBuilder,
    ApplicationInstanceElementNotFound,
    ApplicationInstanceStateError,
)
from di.core.module import Module, ModuleRelated
from di.core.navigator import ApplicationNavigator


class _ComposedAppInspector:
    __slots__ = ("app",)

    def __init__(self, app: ComposedApplication):
        self.app = app

    def assignments_by_elements(self) -> Mapping[Element, Sequence[Assignment]]:
        map_: Dict[Element, List[Assignment]] = {
            element: [] for element in self.import_order_elements()
        }
        for assignment in self.assignments():
            map_[assignment.dependency.source].append(assignment)
        return map_

    def import_order_elements(self) -> Iterable[Element]:
        for step in self.app.import_plan.steps:
            for module in step:
                yield from module.elements

    def assignments(self) -> Iterable[Assignment]:
        for injection_plan in self.app.injection_plans:
            yield from injection_plan.assignments

    def iterate_bootstrap_elements(self) -> Iterable[Element]:
        for module_step in self.app.bootstrap_steps:
            for step in module_step.steps:
                yield from step


class RecursiveProvideContext(ProvideContext):
    def __init__(self, app: ComposedApplication):
        self.global_state: Dict[Element, Any] = {}
        inspector = _ComposedAppInspector(app)
        self._assignments = inspector.assignments_by_elements()
        self._bootstrap_elements = [*inspector.iterate_bootstrap_elements()]

    def boot(self):
        for element in self._bootstrap_elements:
            self.provide(element)

    def eval(self, element: Element):
        if not self.has(element):
            raise ApplicationInstanceStateError(f"Missing element {element}")
        kwargs = self._args_values(element)
        return element.injector(**kwargs)

    def _args_values(self, element: Element) -> Dict[str, Any]:
        return {
            assignment.dependency.arg: assignment.mapper.map(
                [self.provide(value.source) for value in assignment.values]
            )
            for assignment in self._assignments[element]
        }

    def provide(self, element: Element):
        return element.strategy.provide(self, element)

    def has(self, element: Element):
        return element in self._assignments


class RecursiveApplicationInstance(ApplicationInstance):
    def __init__(self, app: ComposedApplication, ctx: RecursiveProvideContext):
        self._navigator = ApplicationNavigator(app.application)
        self._ctx = ctx

    def values_by_type(
        self,
        type_: Type,
        module: Optional[Union[Module, ModuleRelated, str]] = None,
        strict: bool = True,
    ) -> Iterable[Any]:
        elements = self._navigator.by_type(type_=type_, module=module, strict=strict)
        return [self.value_of(element) for element in elements]

    def value_of(self, element: Element):
        if not self._ctx.has(element):
            raise ApplicationInstanceElementNotFound(element=element)
        return self._ctx.provide(element)


class RecursiveApplicationInstanceBuilder(ApplicationInstanceBuilder):
    def __init__(self, app: ComposedApplication):
        self.app = app

    def build(self) -> RecursiveApplicationInstance:
        provide_context = self._provide_context()
        provide_context.boot()
        return RecursiveApplicationInstance(app=self.app, ctx=provide_context)

    def _provide_context(self):
        return RecursiveProvideContext(self.app)
