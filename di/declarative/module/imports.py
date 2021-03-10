from dataclasses import dataclass
from typing import Collection, Iterator, Union

from di.core.module import Module, ModuleRelated
from di.declarative.module.assembly import ModuleAssembly, ModuleImport


@dataclass
class DirectModuleImport(ModuleImport):
    module: Module
    reexport: bool = False

    def solve(self, known: Collection[Module]) -> ModuleAssembly:
        return ModuleAssembly(module=self.module)


@dataclass
class DirectModuleAssemblyImport(ModuleImport):
    assembly: ModuleAssembly

    def solve(self, known: Collection[Module]) -> ModuleAssembly:
        return self.assembly


@dataclass
class NameModuleImport(ModuleImport):
    name: str
    reexport: bool = False

    def solve(self, known: Collection[Module]) -> ModuleAssembly:
        found = [module for module in known if module.name == self.name]
        if not found:
            raise LookupError(f"Module named {self.name} not found")
        if len(found) > 1:
            raise LookupError(
                f"Can not select module from multiple modules named {self.name}"
            )
        return ModuleAssembly(module=found[0])


ModuleImportType = Union[Module, ModuleRelated, ModuleAssembly, ModuleImport, str]


def convert_module_import(module: ModuleImportType, reexport: bool) -> ModuleImport:
    if isinstance(module, ModuleImport):
        return module
    if isinstance(module, ModuleAssembly):
        return DirectModuleAssemblyImport(assembly=module)
    if isinstance(module, str):
        return NameModuleImport(name=module, reexport=reexport)

    if isinstance(module, ModuleRelated):
        module = module.module
    if not isinstance(module, Module):
        raise ValueError(f"expected module but got: {module!r}")
    return DirectModuleImport(module, reexport=reexport)


def convert_module_imports(
    modules: Collection[ModuleImportType],
    reexport: bool = False,
) -> Iterator[ModuleImport]:
    for module in modules:
        yield convert_module_import(module, reexport=reexport)
