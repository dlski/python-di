from typing import Any

from di.core.element import Element, ProvideContext, ProvideStrategy


class SingletonProvideStrategy(ProvideStrategy):
    def provide(self, context: ProvideContext, element: Element) -> Any:
        state = context.global_state
        if element not in state:
            state[element] = context.eval(element)
        return state[element]


class LocalProvideStrategy(ProvideStrategy):
    def provide(self, context: ProvideContext, element: Element) -> Any:
        return context.eval(element)
