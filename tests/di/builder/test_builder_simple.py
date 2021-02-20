from di.builder import AppBuilder
from tests.di.builder import mod_simple, mod_simple_impl


def test_builder_simple_readme_example():
    # Create application builder
    builder = AppBuilder()

    # Create main module and initialize by scraping defined factories
    main = builder.module_builder()
    main.scan_factories([mod_simple, mod_simple_impl])

    # Build app
    instance = builder.build_instance()

    # Get initialized `DomainAction` object
    (action,) = instance.values_by_type(mod_simple.DomainAction)

    # Check app works
    assert action.present() == "Data found: di, test"
