# python-di
Fully automatic dependency injection for python 3.7, 3.8, 3.9 using (not only) type annotations (type hints).

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
from di.builder import AppBuilder
import mod_simple, mod_simple_impl


def main():
    # Create application builder
    builder = AppBuilder()

    # Create main module and initialize by scraping defined factories
    main = builder.module_builder()
    main.scan_factories([mod_simple, mod_simple_impl])

    # Build app
    instance = builder.build_instance()

    # Get initialized `DomainAction` object
    action, = instance.values_by_type(mod_simple.DomainAction)

    # Check app works
    assert action.present() == "Data found: di, test"
```

## More examples
More working examples are available in `tests/di/builder/`.
Please see [tests/di/builder/test_builder.py](tests/di/builder/test_builder.py) for reference.
