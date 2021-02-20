from typing import Collection, Iterable, Sequence

from di.core.app import Application
from di.core.compose.base import (
    AbstractApplicationComposer,
    ApplicationComposerConsistencyError,
    ApplicationComposerModuleAssignmentError,
    ApplicationComposerModuleCyclicDependencyError,
    ApplicationComposerUnresolvedImportError,
    ComposedApplication,
    ModuleBootstrapStep,
    ModuleInjectionPlan,
)
from di.core.element import Element
from di.core.injection import (
    AbstractInjectionSolver,
    InjectionProblem,
    InjectionSolverAssignmentError,
    InjectionSolverCyclicDependencyError,
)
from di.core.module import (
    AbstractModuleElementConsistencyCheck,
    AbstractModuleImportSolver,
    Module,
    ModuleElementConsistencyError,
    ModuleImportPlan,
    ModuleImportSolverError,
)


class ApplicationComposer(AbstractApplicationComposer):
    def __init__(
        self,
        injection_solver: AbstractInjectionSolver,
        import_solver: AbstractModuleImportSolver,
        consistency_check: AbstractModuleElementConsistencyCheck,
    ):
        self.injection_solver = injection_solver
        self.import_solver = import_solver
        self.consistency_check = consistency_check

    def compose(self, application: Application) -> ComposedApplication:
        self._consistency_check(application.modules)
        import_plan = self._module_import_plan(application.modules)
        injection_plans = [*self._iterate_injection_plans(import_plan.steps)]
        bootstrap_steps = [*self._iterate_bootstrap_steps(injection_plans)]
        return ComposedApplication(
            application=application,
            import_plan=import_plan,
            injection_plans=injection_plans,
            bootstrap_steps=bootstrap_steps,
        )

    def _consistency_check(self, modules: Collection[Module]):
        try:
            self.consistency_check.check(modules)
        except ModuleElementConsistencyError:
            raise ApplicationComposerConsistencyError

    def _module_import_plan(self, modules: Collection[Module]) -> ModuleImportPlan:
        try:
            return self.import_solver.solve(modules)
        except ModuleImportSolverError:
            raise ApplicationComposerUnresolvedImportError

    def _iterate_injection_plans(
        self, module_steps: Sequence[Collection[Module]]
    ) -> Iterable[ModuleInjectionPlan]:
        for module_step in module_steps:
            for module in module_step:
                yield self._injection_plan(module)

    def _injection_plan(self, module: Module) -> ModuleInjectionPlan:
        try:
            plan = self.injection_solver.solve(
                InjectionProblem(
                    imports=module.imported_elements,
                    elements=module.elements,
                )
            )
            return ModuleInjectionPlan(
                module=module,
                assignments=plan.assignments,
                graph=plan.graph,
                stages=plan.stages,
            )
        except InjectionSolverAssignmentError as error:
            raise ApplicationComposerModuleAssignmentError(
                module=module,
                dependency=error.dependency,
                msg=str(error),
            )
        except InjectionSolverCyclicDependencyError:
            raise ApplicationComposerModuleCyclicDependencyError(
                module=module,
            )

    def _iterate_bootstrap_steps(
        self, injection_plans: Iterable[ModuleInjectionPlan]
    ) -> Iterable[ModuleBootstrapStep]:
        for injection_plan in injection_plans:
            bootstrap_steps = [*self._iterate_module_bootstrap_steps(injection_plan)]
            if bootstrap_steps:
                yield ModuleBootstrapStep(
                    module=injection_plan.module,
                    steps=bootstrap_steps,
                )

    @classmethod
    def _iterate_module_bootstrap_steps(
        cls, injection_plan: ModuleInjectionPlan
    ) -> Iterable[Collection[Element]]:
        to_bootstrap = injection_plan.module.bootstrap
        for injection_stage in injection_plan.stages:
            bootstrap_stage = to_bootstrap.intersection(injection_stage)
            if bootstrap_stage:
                yield bootstrap_stage
