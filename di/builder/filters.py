from typing import Collection, Optional

from di.utils.inspection.module_factories import (
    FactoryFilter,
    InternalsOrAllFactoryFilter,
    NonAbstractFactoryFilter,
    PublicFactoryFilter,
)
from di.utils.inspection.module_variables import (
    DefinedVariableFilter,
    OptionalAllVariableFilter,
    PublicVariableFilter,
    VariableFilter,
)


class FactoryFilterSets:
    @classmethod
    def domain(cls, filters: Optional[Collection[FactoryFilter]] = None):
        return [
            PublicFactoryFilter(),
            InternalsOrAllFactoryFilter(),
            NonAbstractFactoryFilter(),
            *(filters or ()),
        ]


class VariableFilterSets:
    @classmethod
    def domain(cls, filters: Optional[Collection[VariableFilter]] = None):
        return [
            PublicVariableFilter(),
            OptionalAllVariableFilter(),
            DefinedVariableFilter(),
            *(filters or ()),
        ]
