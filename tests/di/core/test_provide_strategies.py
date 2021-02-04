from typing import Any

from di.core.element import Element, Injector, ProvideContext
from di.core.provide_strategies import LocalProvideStrategy, SingletonProvideStrategy


class SampleContext(ProvideContext):
    def __init__(self):
        self.global_state = {}

    def eval(self, element: Element) -> Any:
        return element.injector()


class SampleInjector(Injector):
    def __call__(self, *args, **kwargs):
        return []


def test_singleton_strategy():
    strategy = SingletonProvideStrategy()
    context = SampleContext()
    element = Element(injector=SampleInjector(), strategy=strategy)

    value1 = strategy.provide(context, element)
    assert isinstance(value1, list)
    assert element in context.global_state
    assert context.global_state[element] is value1

    value2 = strategy.provide(context, element)
    assert value1 is value2


def test_local_strategy():
    strategy = LocalProvideStrategy()
    context = SampleContext()
    element = Element(injector=SampleInjector(), strategy=strategy)

    value1 = strategy.provide(context, element)
    assert isinstance(value1, list)
    assert element not in context.global_state

    value2 = strategy.provide(context, element)
    assert isinstance(value2, list)
    assert element not in context.global_state
    assert value1 is not value2
