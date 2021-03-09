from typing import Collection, Set

from di.core.module import Module


class GlobalRegistry:
    def __init__(self):
        self._modules: Set[Module] = set()
        self._restricted: Set[Module] = set()

    def add(self, module: Module):
        if module in self._modules:
            return
        self._modules.add(module)
        self._restricted.update(self._restricted_from(module))

    @classmethod
    def _restricted_from(cls, global_module: Module):
        yield global_module
        yield from global_module.recursive_imports()

    def all_update(self, scope: Collection[Module]):
        for global_module in self._modules:
            self._add_imports(scope, global_module)

    def _add_imports(self, scope: Collection[Module], global_module: Module):
        restricted = self._restricted
        for module in scope:
            if module not in restricted:
                module.imports.add(global_module)
