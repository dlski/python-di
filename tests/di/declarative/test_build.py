"""
Test file with examples of DI usage.
"""

from di.declarative import (
    DeclarativeApp,
    DeclarativeModule,
    NameModuleImport,
    VariableFilterSets,
    add_factories,
    add_values,
    arg_check,
    scan_factories,
    scan_values,
    type_check,
)
from tests.di.declarative import mod_abstract, mod_config, mod_impl, mod_plugins
from tests.di.declarative.mod_abstract import AllCombinations, DataProvider


def _check_app_works(all_combinations: AllCombinations):
    """
    Tests if `AllCombinations` object is configured properly.
    :param all_combinations: `AllCombinations` object
    """
    combinations = [*all_combinations.all()]
    assert set(combinations) == {
        frozenset(pair)
        for pair in [
            ("1", "A"),
            ("1", "B"),
            ("1", "2"),
            ("A", "B"),
            ("A", "2"),
            ("B", "2"),
        ]
    }


def test_plain():
    """
    Tests application initialized in plain way.
    This example looks simple, but real-world applications are much more complex.
    """

    all_combinations = mod_abstract.AllCombinations(
        config=mod_config.config,
        combinations_generator=mod_impl.ItertoolsGroupCombinationsGenerator(),
        providers=[mod_plugins.LetterDataProvider(), mod_plugins.NumberDataProvider()],
    )
    _check_app_works(all_combinations)


def test_build_manual():
    """
    Creates application using declarative containers
    with manual control of used components.
    """

    # Create application definition by creating `DeclarativeApp` object
    app_def = DeclarativeApp(
        # Add logical module config
        DeclarativeModule(
            # Add module components - specified list of values
            add_values(mod_config.config),
            # Set name to "config"
            name="config",
        ),
        # Add logical module main
        DeclarativeModule(
            # Add module components - specified list of factories
            add_factories(
                mod_abstract.AllCombinations,
                mod_impl.ItertoolsGroupCombinationsGenerator,
                mod_plugins.LetterDataProvider,
                mod_plugins.NumberDataProvider,
            ),
            # Import config module by name
            imports=["config"],
            # Set name to main
            name="main",
        ),
        # Add argument aggregation of `DataProvider` collection
        agg_checks=[type_check(DataProvider)],
    )

    # This operation builds application instance:
    # - solves module dependency graph
    # - solves in module dependency injection sub-graphs
    # - initializes factories dependency injection chain
    # - calls factories marked by `bootstrap` option
    instance = app_def.build_instance()
    # This operation creates/gets `AllCombinations` provided
    # by automatic dependency injection mechanism.
    (all_combinations,) = instance.values_by_type(mod_abstract.AllCombinations)

    # Check initialized application.
    _check_app_works(all_combinations)


def test_build_scan():
    """
    Creates application using declarative containers
    with automatic control of used components.
    """

    # Create application definition part by part
    # Create logical module config
    config = DeclarativeModule(
        # Scan for all values in `mod_config` using specified filter sets (optional)
        scan_values(mod_config, filter_sets=[VariableFilterSets.domain()]),
        # Set name config
        name="config",
    )
    # Create logical module main
    main = DeclarativeModule(
        # Add factory to module with aggregation in argument named "providers"
        add_factories(
            mod_abstract.AllCombinations, agg_checks=[arg_check("providers")]
        ),
        # Scan for all factories in `mod_impl` and `mod_plugins`
        scan_factories(mod_impl, mod_plugins),
        # Import config module by reference
        imports=[config],
        # Set name to main
        name="main",
    )
    # Create app definition.
    # NOTE:
    # By default application option `follow_imports` is `True`,
    # which means that modules recursively imported,
    # but not provided in app definition will be added automatically.
    app_def = DeclarativeApp(main)

    # This operation builds application instance:
    # - solves module dependency graph
    # - solves in module dependency injection sub-graphs
    # - initializes factories dependency injection chain
    # - calls factories marked by `bootstrap` option
    instance = app_def.build_instance()
    # This operation creates/gets `AllCombinations` provided
    # by automatic dependency injection mechanism.
    (all_combinations,) = instance.values_by_type(mod_abstract.AllCombinations)

    # Check initialized application.
    _check_app_works(all_combinations)


def test_build_simplified():
    """
    Creates application using declarative with automatic control of used components.
    Simplified example.
    """

    # Create single module application
    app_def = DeclarativeApp(
        DeclarativeModule(
            # Scan for values and factories in pointed modules
            scan_values(mod_config),
            scan_factories(mod_abstract, mod_impl, mod_plugins),
        ),
        # Add argument aggregation of `DataProvider` collection
        agg_checks=[type_check(DataProvider)],
    )

    # This operation builds application instance:
    # - solves module dependency graph
    # - solves in module dependency injection sub-graphs
    # - initializes factories dependency injection chain
    # - calls factories marked by `bootstrap` option
    instance = app_def.build_instance()
    # This operation creates/gets `AllCombinations` provided
    # by automatic dependency injection mechanism.
    (all_combinations,) = instance.values_by_type(mod_abstract.AllCombinations)

    # Check initialized application.
    _check_app_works(all_combinations)


def test_build_globals():
    """
    Creates application using declarative with automatic control of used components.
    Uses global flag and reexport in modules.
    """

    # Create application.
    # NOTE: Modules with `global_=True` will be imported automatically
    #       by other non global related modules.
    # NOTE: Reexport flag will take all imported module exports
    #       and appends to exports in current module.
    #       Works like exported elements forwarding.
    app_def = DeclarativeApp(
        DeclarativeModule(
            scan_values(mod_config),
            global_=True,
        ),
        DeclarativeModule(
            scan_factories(mod_plugins),
            name="plugins",
        ),
        DeclarativeModule(
            scan_factories(mod_impl),
            imports=[NameModuleImport("plugins", reexport=True)],
            global_=True,
        ),
        DeclarativeModule(
            scan_factories(mod_abstract),
        ),
        agg_checks=[type_check(DataProvider)],
    )

    # This operation builds application instance and gets `AllCombinations` object
    instance = app_def.build_instance()
    (all_combinations,) = instance.values_by_type(mod_abstract.AllCombinations)

    # Check initialized application.
    _check_app_works(all_combinations)
