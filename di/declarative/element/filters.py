from typing import Collection, Optional, Union

from di.utils.inspection.module_factories import (
    FactoryFilter,
    InternalsOrAllFactoryFilter,
    NonAbstractFactoryFilter,
    NonTypeFactoryFilter,
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
    def domain(
        cls,
        filters: Optional[Collection[FactoryFilter]] = None,
        before: Collection[FactoryFilter] = (),
        exclude_types: Optional[Union[type, Collection[type]]] = None,
    ):
        if exclude_types:
            before = [NonTypeFactoryFilter(exclude_types), *before]
        return [
            *before,
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
