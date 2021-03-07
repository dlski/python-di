from collections import defaultdict
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Collection, DefaultDict, Iterable, List, Mapping

from di.core.element import Element
from di.core.module import Module, ModuleRelated
from di.declarative.aggregation import IsAggregationType


@dataclass
class ModuleProperties:
    global_: bool = False
    module_agg: Collection[IsAggregationType] = ()
    element_agg: Mapping[Element, Collection[IsAggregationType]] = MappingProxyType({})


@dataclass
class MutableModuleProperties(ModuleProperties):
    module_agg: List[IsAggregationType] = field(default_factory=list)
    element_agg: DefaultDict[Element, List[IsAggregationType]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_element_agg(self, element: Element, checks: Iterable[IsAggregationType]):
        self.element_agg[element].extend(checks)


class ModuleAssembly(ModuleRelated):
    forward_imports: List["ModuleImport"]

    def __init__(
        self,
        module: Module,
        forward_imports: Iterable["ModuleImport"] = (),
        properties: ModuleProperties = ModuleProperties(),
    ):
        self.module = module
        self.forward_imports = [*forward_imports]
        self.properties = properties


class ModuleImport:
    reexport: bool = False

    def solve(self, known: Collection[Module]) -> ModuleAssembly:
        raise NotImplementedError
