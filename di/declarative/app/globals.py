from typing import Collection, Dict

from di.core.module import Module


class GlobalModuleEntry:
    def __init__(self, module: Module):
        self.module = module
        self.restricted: Collection[Module] = {module, *module.recursive_imports()}

    def update(self, scope: Collection[Module]):
        for module in scope:
            if module not in self.restricted:
                module.imports.add(self.module)


class GlobalRegistry:
    def __init__(self):
        self._map: Dict[Module, GlobalModuleEntry] = {}

    def add(self, module: Module) -> GlobalModuleEntry:
        if module in self._map:
            return self._map[module]
        entry = GlobalModuleEntry(module)
        self._map[module] = entry
        return entry

    def all_update(self, scope: Collection[Module]):
        for entry in self._map.values():
            entry.update(scope)
