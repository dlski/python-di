from dataclasses import dataclass, field
from typing import Collection, Iterable, Optional, Sequence, Set

from di.core.element import Element
from di.utils.graph import DirectionalGraph, DirectionalGraphEdge


@dataclass
class Module:
    name: Optional[str] = None
    elements: Set[Element] = field(default_factory=set)
    bootstrap: Set[Element] = field(default_factory=set)
    imports: Set["Module"] = field(default_factory=set)
    exports: Set[Element] = field(default_factory=set)

    @property
    def imported_elements(self) -> Set[Element]:
        return {*self.iterate_imported_elements()}

    def iterate_imported_elements(self) -> Iterable[Element]:
        for module in self.imports:
            yield from module.exports

    def recursive_imports(self) -> Set["Module"]:
        visited = set()
        to_visit = set(self.imports)
        while to_visit:
            next_ = to_visit.pop()
            if next_ in visited:
                continue
            visited.add(next_)
            to_visit.update(next_.imports)
        return visited

    __hash__ = object.__hash__
    __eq__ = object.__eq__


class ModuleRelated:
    module: Module


class ModuleImportGraphEdge(DirectionalGraphEdge[Module]):
    __slots__ = "source", "target"

    def __init__(self, source: Module, target: Module):
        self.source = source
        self.target = target


ModuleImportGraph = DirectionalGraph[Module, ModuleImportGraphEdge]


@dataclass
class ModuleImportPlan:
    graph: ModuleImportGraph
    steps: Sequence[Collection[Module]]


class ModuleImportSolverError(Exception):
    pass


class AbstractModuleImportSolver:
    def solve(self, modules: Collection[Module]) -> ModuleImportPlan:
        raise NotImplementedError


class ModuleElementConsistencyError(Exception):
    pass


class AbstractModuleElementConsistencyCheck:
    def check(self, modules: Collection[Module]):
        raise NotImplementedError
