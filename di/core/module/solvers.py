import itertools
from typing import Collection, Sequence

from di.core.module.base import (
    AbstractModuleElementConsistencyCheck,
    AbstractModuleImportSolver,
    Module,
    ModuleElementConsistencyError,
    ModuleImportGraph,
    ModuleImportGraphEdge,
    ModuleImportPlan,
    ModuleImportSolverError,
)
from di.utils.graph import (
    DirectionalGraph,
    DirectionalGraphIteratorError,
    DirectionalGraphTopologyIterator,
)


class ModuleImportSolver(AbstractModuleImportSolver):
    def solve(self, modules: Collection[Module]) -> ModuleImportPlan:
        graph = self._create_graph(modules)
        steps = self._steps(graph)
        return ModuleImportPlan(
            graph=graph,
            steps=steps,
        )

    @classmethod
    def _create_graph(cls, modules: Collection[Module]):
        return DirectionalGraph(
            nodes=modules,
            edges=cls._create_graph_edges(modules),
        )

    @classmethod
    def _create_graph_edges(cls, modules: Collection[Module]):
        for module in modules:
            for imported_module in module.imports:
                yield ModuleImportGraphEdge(module, imported_module)

    @staticmethod
    def _steps(graph: ModuleImportGraph) -> Sequence[Collection[Module]]:
        try:
            return [*DirectionalGraphTopologyIterator(graph)]
        except DirectionalGraphIteratorError:
            raise ModuleImportSolverError("Module cyclic import problem")


class ModuleElementConsistencyCheck(AbstractModuleElementConsistencyCheck):
    def check(self, modules: Collection[Module]):
        for module in modules:
            self._check_module_exports(module)
            self._check_module_bootstrap(module)
        self._check_duplicates(modules)

    @classmethod
    def _check_module_exports(cls, module: Module):
        all_elements = {*module.elements, *module.imported_elements}
        if not module.exports.issubset(all_elements):
            difference = module.exports - all_elements
            raise ModuleElementConsistencyError(
                f"Module {module} exports non accessible elements: {difference}"
            )

    @classmethod
    def _check_module_bootstrap(cls, module: Module):
        if not module.bootstrap.issubset(module.elements):
            difference = module.bootstrap - module.elements
            raise ModuleElementConsistencyError(
                f"Module {module} bootstraps not owned elements: {difference}"
            )

    @classmethod
    def _check_duplicates(cls, modules: Collection[Module]):
        for a, b in itertools.combinations(modules, 2):
            if not a.elements.isdisjoint(b.elements):
                common = a.elements & b.elements
                raise ModuleElementConsistencyError(
                    f"Module {a} and {b} uses the same elements: {common}"
                )
