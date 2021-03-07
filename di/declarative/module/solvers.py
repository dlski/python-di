from dataclasses import dataclass
from typing import Collection, Dict, Iterator, Sequence, Set, Tuple

from di.core.module import Module
from di.declarative.module.assembly import ModuleAssembly, ModuleImport


class ModuleAssemblySolver:
    def solve(
        self, known: Collection[Module], assembly: ModuleAssembly
    ) -> Collection[ModuleAssembly]:
        raise NotImplementedError


class StrictModuleAssemblySolver(ModuleAssemblySolver):
    def solve(
        self, known: Collection[Module], assembly: ModuleAssembly
    ) -> Collection[ModuleAssembly]:
        imported_modules = [
            next_.module for next_ in self._assemblies(known, assembly.forward_imports)
        ]
        assembly.module.imports.update(imported_modules)
        assembly.forward_imports.clear()
        return [assembly]

    @staticmethod
    def _assemblies(
        known: Collection[Module], forward_imports: Sequence[ModuleImport]
    ) -> Iterator[ModuleAssembly]:
        for import_ in forward_imports:
            next_assembly = import_.solve(known)
            yield next_assembly


class RecursiveModuleAssemblySolver(ModuleAssemblySolver):
    def solve(
        self, known: Collection[Module], assembly: ModuleAssembly
    ) -> Collection[ModuleAssembly]:
        actions, to_add = _ModuleSolver(known=known, initial=assembly).solve()
        for action in actions:
            action.run()
        return to_add


class _Action:
    def run(self):
        raise NotImplementedError


@dataclass
class _AddModuleImportAction(_Action):
    what: Module
    to: Module
    import_: ModuleImport

    def run(self):
        to = self.to
        what = self.what

        to.imports.add(what)
        if self.import_.reexport:
            to.exports.update(what.exports)


@dataclass
class _ClearForwardImportsAction(_Action):
    asm: ModuleAssembly

    def run(self):
        self.asm.forward_imports.clear()


class _ModuleSolver:
    __slots__ = "_initial", "_visited", "_known", "_map"

    def __init__(self, known: Collection[Module], initial: ModuleAssembly):
        self._initial = initial
        self._visited: Set[Module] = {initial.module}
        self._known: Set[Module] = {initial.module, *known}
        self._map: Dict[Module, ModuleAssembly] = {}

    def solve(self) -> Tuple[Sequence[_Action], Collection[ModuleAssembly]]:
        actions = [*self._actions(self._initial)]
        assemblies = self._visited_assemblies()
        return actions, assemblies

    def _actions(self, asm: ModuleAssembly) -> Iterator[_Action]:
        module = asm.module
        self._map[module] = asm
        for import_ in asm.forward_imports:
            next_ = import_.solve(self._known)
            next_module = next_.module
            if next_module not in self._visited:
                self._visited.add(next_module)
                self._known.add(next_module)
                yield from self._actions(next_)
            yield _AddModuleImportAction(what=next_module, to=module, import_=import_)
        if asm.forward_imports:
            yield _ClearForwardImportsAction(asm=asm)

    def _visited_assemblies(self) -> Collection[ModuleAssembly]:
        _map = self._map
        return [_map[module] for module in self._visited]
