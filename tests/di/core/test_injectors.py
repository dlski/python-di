from di.core.injectors import FactoryInjector, ValueInjector


class X:
    def __init__(self):
        pass


class Y:
    def __init__(self, x: X, extra: str = "extra"):
        self.x = x
        self.extra = extra


def y(x: X, extra: str = "extra") -> Y:
    return Y(x, extra)


def y_str(x: "X", extra: str = "extra") -> Y:
    return Y(x, extra)


def _functional_test_factory_injector(provider: FactoryInjector):
    dependencies = list(provider.dependencies())
    assert len(dependencies) == 2
    assert dependencies[0].arg == "x"
    assert dependencies[0].type == X
    assert dependencies[0].mandatory
    assert dependencies[1].arg == "extra"
    assert dependencies[1].type == str
    assert not dependencies[1].mandatory


def test_type_factory_injector():
    injector = FactoryInjector(Y)

    _functional_test_factory_injector(injector)


def test_fn_factory_injector():
    injector = FactoryInjector(y)
    _functional_test_factory_injector(injector)


def test_fn_str_factory_injector():
    injector = FactoryInjector(y_str)
    _functional_test_factory_injector(injector)


def test_value_injector():
    x = X()
    target_value_injector = ValueInjector(x)
    assert target_value_injector() == x

    result = target_value_injector.result()
    assert result
    assert result.type == X
