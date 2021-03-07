from typing import Iterable

from di.core.app import Application, ApplicationRelated
from di.core.compose import ApplicationComposer, ComposedApplication
from di.core.injection import InjectionSolver
from di.core.instance import ApplicationInstance, RecursiveApplicationInstanceBuilder
from di.core.module import ModuleElementConsistencyCheck, ModuleImportSolver
from di.declarative.aggregation import AggRegistry, IsAggregationType
from di.declarative.app.globals import GlobalRegistry
from di.declarative.module import (
    ModuleAssembly,
    RecursiveModuleAssemblySolver,
    StrictModuleAssemblySolver,
)


class DeclarativeApp(ApplicationRelated):
    def __init__(
        self,
        *modules: ModuleAssembly,
        agg_checks: Iterable[IsAggregationType] = (),
        follow_imports: bool = True
    ):
        self.app = Application()

        if follow_imports:
            self._solver = RecursiveModuleAssemblySolver()
        else:
            self._solver = StrictModuleAssemblySolver()
        self._global_registry = GlobalRegistry()
        self._agg_registry = AggRegistry()
        self._agg_registry.include_globals(agg_checks)
        self._modules = modules

        self._init()

    def _init(self):
        for module in self._modules:
            self._process(module)
        self._global_registry.all_update(self.app.modules)

    def _process(self, asm: ModuleAssembly):
        app_modules = self.app.modules
        to_add = self._solver.solve(app_modules, asm)
        for _next in to_add:
            self._add(_next)

    def _add(self, asm: ModuleAssembly):
        module = asm.module
        self.app.modules.add(module)

        properties = asm.properties
        if properties.global_:
            self._global_registry.add(module)
        self._agg_registry.add_module(module, properties.module_agg)
        self._agg_registry.include_elements(properties.element_agg.items())

    def build_instance(self) -> ApplicationInstance:
        composed = self.build_composed()
        return RecursiveApplicationInstanceBuilder(composed).build()

    def build_composed(self) -> ComposedApplication:
        agg_selector = self._agg_registry.build_selector()
        composer = ApplicationComposer(
            InjectionSolver(factory_selector=agg_selector),
            ModuleImportSolver(),
            ModuleElementConsistencyCheck(),
        )
        return composer.compose(self.app)
