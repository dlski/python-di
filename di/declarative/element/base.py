from dataclasses import dataclass
from typing import Collection, Iterator, Optional

from di.core.element import Element, Injector
from di.core.provide_strategies import LocalProvideStrategy, SingletonProvideStrategy
from di.declarative.aggregation import IsAggregationType


@dataclass
class ModuleElement:
    element: Element
    export: bool = True
    bootstrap: bool = False
    agg_checks: Collection[IsAggregationType] = ()

    @classmethod
    def create(
        cls,
        injector: Injector,
        singleton: bool = True,
        label: Optional[str] = None,
        export: bool = True,
        bootstrap: bool = False,
        agg_checks: Collection[IsAggregationType] = (),
    ) -> "ModuleElement":
        if singleton:
            strategy = SingletonProvideStrategy()
        else:
            strategy = LocalProvideStrategy()
        return cls(
            element=Element(
                injector=injector,
                strategy=strategy,
                label=label,
            ),
            export=export,
            bootstrap=bootstrap,
            agg_checks=agg_checks,
        )


class ModuleElementIterable:
    def __iter__(self) -> Iterator[ModuleElement]:
        raise NotImplementedError
