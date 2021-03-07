from di.declarative import DeclarativeApp, DeclarativeModule, scan_factories
from tests.di.declarative import mod_simple, mod_simple_impl


def test_build_simple_readme_example():
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
    (action,) = instance.values_by_type(mod_simple.DomainAction)

    # check app works
    assert action.present() == "Data found: di, test"
