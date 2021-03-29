# python-di

[![CI](https://github.com/dlski/python-di/actions/workflows/ci.yml/badge.svg?branch=master&event=push)](https://github.com/dlski/python-di/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dlski/python-di/branch/master/graph/badge.svg?token=DXIZA2T8W6)](https://codecov.io/gh/dlski/python-di)
[![pypi](https://img.shields.io/pypi/v/python-di.svg)](https://pypi.python.org/pypi/python-di)
[![downloads](https://img.shields.io/pypi/dm/python-di.svg)](https://pypistats.org/packages/python-di)
[![versions](https://img.shields.io/pypi/pyversions/python-di.svg)](https://github.com/dlski/python-di)
[![license](https://img.shields.io/github/license/dlski/python-di.svg)](https://github.com/dlski/python-di/blob/master/LICENSE)

Fully automatic dependency injection for python 3.7, 3.8, 3.9, pypy3 using (not only) argument annotations / type hints.

Corresponds to clean architecture patterns and ideal for business applications created in DDD / Hexagonal architecture flavour.
No external dependencies - uses only standard libraries.

Key features:
- automatic type matching based on type hints / type annotations - 
  no manual configuration is needed, it just works out of the box
- configurable object aggregation injection - 
  DI can join `SomeClass` objects and inject into argument annotated as `Collection[SomeClass]`
- not harm existing codebase - 
  no decorators, no extra metadata are needed in existing codebase to make app construction possible
- no singletons or global DI process state -
  app or any app components can be instantiated independently as many times as needed
- transparency of DI process - 
  static dependency graph and injection plan is built, informative exceptions on error cases
  (like cyclic dependency or missing elements)

## Help
Coming soon...

## An Example
Application domain located in `mod_simple.py`:
```py
from typing import List


class Repo:
    def read(self) -> List[str]:
        raise NotImplementedError


class DomainAction:
    def __init__(self, repo: Repo):
        self.repo = repo

    def present(self) -> str:
        joined = ", ".join(self.repo.read())
        return f"Data found: {joined}"
```

Application concretes located in `mod_simple_impl.py`:
```py
from typing import List

from mod_simple import Repo


class MockupRepo(Repo):
    def read(self) -> List[str]:
        return ["di", "test"]
```

Automatic application construction:
```py
from di.declarative import DeclarativeApp, DeclarativeModule, scan_factories
import mod_simple, mod_simple_impl


def main():
    # create app definition
    app_def = DeclarativeApp(
        DeclarativeModule(
            # automatically add factories from `mod_simple` and `mod_simple_impl`
            scan_factories(mod_simple, mod_simple_impl),
        )
    )

    # build app
    instance = app_def.build_instance()

    # get initialized `DomainAction` object
    action, = instance.values_by_type(mod_simple.DomainAction)

    # check app works
    assert action.present() == "Data found: di, test"
```

## More examples
More working examples are available in `tests/di/declarative/`.
Please see [tests/di/declarative/test_build.py](tests/di/declarative/test_build.py) for reference.
