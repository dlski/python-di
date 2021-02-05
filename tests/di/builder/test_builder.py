"""
Test file with examples of DI usage.
"""

from di.builder.app import AppBuilder
from di.builder.filters import FactoryFilterSets, VariableFilterSets
from tests.di.builder import mod_abstract, mod_config, mod_impl, mod_plugins
from tests.di.builder.mod_abstract import AllCombinations, DataProvider


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
    Manual initialization code and its maintenance may cost a lot of work.
    """

    all_combinations = mod_abstract.AllCombinations(
        config=mod_config.config,
        combinations_generator=mod_impl.ItertoolsGroupCombinationsGenerator(),
        providers=[mod_plugins.LetterDataProvider(), mod_plugins.NumberDataProvider()],
    )
    _check_app_works(all_combinations)


def test_builder_manual():
    """
    Creates application using builder with manual control of used components.
    """

    # First of all create application builder.
    builder = AppBuilder()

    # Lets create config module, that will contain initialized `Config` object.
    config_module = builder.module_builder("config")
    # Add initialized config value.
    # ---
    # By default option `export` in `add_values` is set,
    # so this value will be visible in other modules
    # that import this module.
    config_module.add_values(mod_config.config)

    # Lets create system module,
    # that will contain domain with connected concrete objects.
    system_module = builder.module_builder("system")
    # Import `config_module` by `system_module`.
    system_module.imports(config_module)
    # Add factory for `AllCombinations`.
    # ---
    # DI mechanism will try to call this factory (create class instance),
    # injecting into arguments objects, by type annotations matching.
    all_combinations_element = system_module.add_factory(mod_abstract.AllCombinations)
    # Add factory for concrete `ItertoolsGroupCombinationsGenerator`.
    system_module.add_factory(mod_impl.ItertoolsGroupCombinationsGenerator)

    # As an example mark that all `DataProvider` objects can be aggregated
    # and injected into argument, where its type annotation
    # refers to any kind of `DataProvider` collection.
    builder.add_aggregation_type(DataProvider)

    # Add factories for `DataProvider` concretes.
    system_module.add_factories(
        mod_plugins.LetterDataProvider,
        mod_plugins.NumberDataProvider,
    )

    # This operation builds application instance:
    # - solves module dependency graph
    # - solves in module dependency injection sub-graphs
    # - initializes factories dependency injection chain
    # - calls factories marked by `bootstrap` option
    instance = builder.build_instance()
    # This operation creates/gets `AllCombinations` provided
    # by automatic dependency injection mechanism.
    # ---
    # Particular value can be retrieved using some kind of pointer
    # returned by any `add_` operation like above.
    all_combinations = instance.value_of(all_combinations_element)

    # Check initialized application.
    _check_app_works(all_combinations)


def test_builder_scan():
    """
    Creates application using builder with automatic control of used components.
    """

    # First of all create application builder.
    builder = AppBuilder()

    # Lets create config module, that will contain initialized `Config` object.
    config_module = builder.module_builder("config")
    # Add initialized config value.
    # ---
    # Scan for all values in python module, that passes by filter cascade
    # defined as `VariableFilterSets.domain()`.
    # `VariableFilterSets.domain()` returns cascade, that contains:
    # - PublicVariableFilter - filters only public variables (by name)
    # - OptionalAllVariableFilter - filters only variables in __all__ attribute
    #   (if __all__ is present in module)
    # - DefinedVariableFilter - filters only variables with defined value
    #   (variables marked only by annotation are iterated too)
    # ---
    # By default option `export` in `add_values` is set,
    # so this value will be visible in other modules
    # that import this module.
    config_module.scan_values(mod_config, VariableFilterSets.domain())

    # Lets create system module,
    # that will contain domain with connected concrete objects.
    system_module = builder.module_builder("system")
    # Import `config_module` by `system_module`.
    system_module.imports(config_module)
    # Add factory for `AllCombinations`.
    # ---
    # DI mechanism will try to call this factory (create class instance),
    # injecting into arguments objects, by type annotations matching.
    all_combinations_element = system_module.add_factory(mod_abstract.AllCombinations)

    # As an example, mark argument named `providers` of `AllCombinations` factory
    # to inject collection of objects described by argument type annotation -
    # in this case aggregated all available `DataProvider` objects in scope.
    # ---
    # In previous example we marked `DataProvider` objects can be aggregated
    # into collection (if necessary) in every argument with `DataProvider`
    # collection type annotation.
    # In this case aggregation of `DataProvider` objects can be used
    # only in specified argument and specified factory case
    # (and proper type annotation).
    builder.add_aggregation_spec(all_combinations_element, "providers")

    # Automatically add factories (classes and functions)
    # found in `mod_impl` and `mod_plugins` python modules.
    # To filter only public concretes `FactoryFilterSets.domain()` filter cascade
    # is used.
    # `FactoryFilterSets.domain()` returns cascade, that contains:
    # - PublicFactoryFilter - filters only public variables (by name)
    # - InternalsOrAllFactoryFilter - filters only factories defined in this module
    #   or specified in __all__ module attribute
    # - NonAbstractFactoryFilter - filters only concretes, skips abstract classes;
    #   by default duck typed abstract class check is used,
    #   that refers to methods/properties with `raise NotImplementedError` code
    system_module.scan_factories([mod_impl, mod_plugins], FactoryFilterSets.domain())

    # This operation builds application instance:
    # - solves module dependency graph
    # - solves in module dependency injection sub-graphs
    # - initializes factories dependency injection chain
    # - calls factories marked by `bootstrap` option
    instance = builder.build_instance()
    # This operation creates/gets `AllCombinations` provided
    # by automatic dependency injection mechanism.
    # ---
    # Particular value can be retrieved using some kind of pointer
    # returned by any `add_` operation like above.
    all_combinations = instance.value_of(all_combinations_element)

    # Check initialized application.
    _check_app_works(all_combinations)


def test_builder_simplified():
    """
    Creates application using builder with automatic control of used components.
    Simplified example.
    """

    # First of all create application builder.
    builder = AppBuilder()

    # Create main module and add application ingredients
    main = builder.module_builder()
    main.scan_values(mod_config)
    main.scan_factories([mod_abstract, mod_impl, mod_plugins])

    # Setup aggregation of `DataProvider` (see detailed examples above)
    builder.add_aggregation_type(DataProvider)

    # Create instance
    instance = builder.build_instance()
    # Get object value
    (all_combinations,) = instance.values_by_type(mod_abstract.AllCombinations)

    # Check initialized application.
    _check_app_works(all_combinations)
