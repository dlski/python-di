from typing import Collection, Iterable, List, Optional, cast

from di.core.module import Module
from di.declarative.aggregation import IsAggregationType
from di.declarative.element import ModuleElement
from di.declarative.module.assembly import MutableModuleProperties
from di.declarative.module.imports import (
    ModuleAssembly,
    ModuleImport,
    ModuleImportType,
    convert_module_imports,
)


class DeclarativeModule(ModuleAssembly):
    forward_imports: List[ModuleImport]

    def __init__(
        self,
        *iterables: Iterable[ModuleElement],
        imports: Collection[ModuleImportType] = (),
        name: Optional[str] = None,
        global_: bool = False,
        agg_checks: Iterable[IsAggregationType] = (),
    ):
        super().__init__(
            module=Module(name=name),
            properties=MutableModuleProperties(
                global_=global_, module_agg=[*agg_checks]
            ),
        )
        self._imports(*imports)
        self._include(*iterables)

    def _imports(self, *imports: ModuleImportType, reexport: bool = False):
        self.forward_imports.extend(convert_module_imports(imports, reexport=reexport))

    def _include(self, *iterables: Iterable[ModuleElement]):
        properties = cast(MutableModuleProperties, self.properties)
        elements = self.module.elements
        exports = self.module.exports
        bootstrap = self.module.bootstrap

        for iterable in iterables:
            for module_element in iterable:
                element = module_element.element
                elements.add(element)
                if module_element.export:
                    exports.add(element)
                if module_element.bootstrap:
                    bootstrap.add(element)
                if module_element.agg_checks:
                    properties.add_element_agg(element, module_element.agg_checks)
