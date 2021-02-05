from typing import Any, Collection, Optional

from di.builder.assignment import (
    AggregationAssignmentFactorySelector,
    AggTypeDependencyCheck,
    ArgDependencyCheck,
)
from di.builder.module import AppModuleBuilder
from di.core.app import Application, ApplicationRelated
from di.core.compose.base import ComposedApplication
from di.core.compose.composers import ApplicationComposer
from di.core.element import Element
from di.core.injection.solvers import InjectionSolver
from di.core.instance.base import ApplicationInstance
from di.core.instance.recurrent import RecurrentApplicationInstanceBuilder
from di.core.module.base import Module
from di.core.module.solvers import ModuleElementConsistencyCheck, ModuleImportSolver


class AppBuilder(ApplicationRelated):
    def __init__(self, aggregation_types: Optional[Collection[Any]] = None):
        self.app = Application()
        self.assignment_factory_selector = AggregationAssignmentFactorySelector(
            aggregation_checks=[
                AggTypeDependencyCheck(aggregation_type)
                for aggregation_type in (aggregation_types or ())
            ]
        )

    def add_aggregation_type(self, type_spec: Any):
        self.assignment_factory_selector.add_aggregation_check(
            AggTypeDependencyCheck(type_spec)
        )

    def add_aggregation_spec(self, element: Element, arg: str):
        self.assignment_factory_selector.add_aggregation_check(
            ArgDependencyCheck(element, arg)
        )

    def module_builder(self, name: Optional[str] = None):
        module = Module(name=name)
        self.app.modules.add(module)
        return AppModuleBuilder(module)

    def build_instance(self) -> ApplicationInstance:
        composed = self.build_composed()
        return RecurrentApplicationInstanceBuilder(composed).build()

    def build_composed(self) -> ComposedApplication:
        composer = ApplicationComposer(
            InjectionSolver(factory_selector=self.assignment_factory_selector),
            ModuleImportSolver(),
            ModuleElementConsistencyCheck(),
        )
        return composer.compose(self.app)
