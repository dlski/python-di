from dataclasses import dataclass
from typing import Sequence, Set

from di.core.app import Application
from di.core.element import Dependency, Element
from di.core.injection import InjectionPlan
from di.core.module import Module, ModuleImportPlan


@dataclass
class ModuleInjectionPlan(InjectionPlan):
    module: Module


@dataclass
class ModuleBootstrapStep:
    module: Module
    steps: Sequence[Set[Element]]


@dataclass
class ComposedApplication:
    application: Application
    import_plan: ModuleImportPlan
    injection_plans: Sequence[ModuleInjectionPlan]
    bootstrap_steps: Sequence[ModuleBootstrapStep]


class ApplicationComposerError(Exception):
    pass


class ApplicationComposerConsistencyError(ApplicationComposerError):
    pass


class ApplicationComposerUnresolvedImportError(ApplicationComposerError):
    pass


class ApplicationComposerModuleAssignmentError(ApplicationComposerError):
    def __init__(self, module: Module, dependency: Dependency, msg: str):
        super().__init__(f"In module {module}: {msg}")
        self.module = module
        self.dependency = dependency


class ApplicationComposerModuleCyclicDependencyError(ApplicationComposerError):
    def __init__(self, module: Module):
        super().__init__(f"Cyclic dependency problem in {module}")
        self.module = module


class AbstractApplicationComposer:
    def compose(self, application: Application) -> ComposedApplication:
        raise NotImplementedError
