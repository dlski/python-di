import inspect
from typing import Any, Dict

import pytest

from di.utils.inspection.abstract import AbstractInspector
from tests.di.utils.inspection.module_abstract import (
    CanonicalAbstract,
    DuckAbstract1,
    DuckAbstract2,
    DuckAbstract3,
    DuckAbstract4,
    DuckAbstract5,
    NormalClass,
    abstract_async_fn,
    abstract_fn,
    normal_async_fn,
    normal_fn,
)


def test_abstract_functions():
    assert not AbstractInspector.is_abstract_function(normal_fn)
    assert AbstractInspector.is_abstract_function(abstract_fn)
    assert not AbstractInspector.is_abstract_function(normal_async_fn)
    assert AbstractInspector.is_abstract_function(abstract_async_fn)


def test_abstract_classes():
    assert not AbstractInspector.is_abstract_class(NormalClass)
    assert AbstractInspector.is_abstract_class(CanonicalAbstract)
    assert AbstractInspector.is_abstract_class(DuckAbstract1)
    assert AbstractInspector.is_abstract_class(DuckAbstract2)
    assert AbstractInspector.is_abstract_class(DuckAbstract3)
    assert AbstractInspector.is_abstract_class(DuckAbstract4)
    assert AbstractInspector.is_abstract_class(DuckAbstract5)


@pytest.fixture(scope="module")
def module_globals():
    _globals = {}
    from tests.di.utils.inspection import module_abstract

    # noinspection PyTypeChecker
    exec(inspect.getsource(module_abstract), _globals)
    return _globals


def test_abstract_dynamic(module_globals: Dict[str, Any]):
    assert not AbstractInspector.is_abstract_class(module_globals[NormalClass.__name__])
    assert AbstractInspector.is_abstract_class(
        module_globals[CanonicalAbstract.__name__]
    )
    assert AbstractInspector.is_abstract_class(module_globals[DuckAbstract1.__name__])
    assert AbstractInspector.is_abstract_class(module_globals[DuckAbstract2.__name__])
    assert AbstractInspector.is_abstract_class(module_globals[DuckAbstract3.__name__])
    assert AbstractInspector.is_abstract_class(module_globals[DuckAbstract4.__name__])
    assert AbstractInspector.is_abstract_class(module_globals[DuckAbstract5.__name__])
