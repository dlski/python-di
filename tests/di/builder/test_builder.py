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
    # so this value will be visible
    # when this module will be imported by another module.
    config_module.add_values(mod_config.config)

    # Lets create system module,
    # that will contain domain with connected concrete objects.
    system_module = builder.module_builder("system")
    # Add `config_module` to `system_module` imported modules.
    system_module.imports(config_module)
    # Add factory for `AllCombinations`.
    # ---
    # DI mechanism will try to call (create) this factory,
    # injecting non-abstract arguments matching type annotations.
    all_combinations_element = system_module.add_factory(mod_abstract.AllCombinations)
    # Add factory for concrete `ItertoolsGroupCombinationsGenerator`.
    system_module.add_factory(mod_impl.ItertoolsGroupCombinationsGenerator)

    # As an example mark that all `DataProvider` objects can be aggregated
    # and injected into argument,
    # where its type annotation refers to collection of `DataProvider`.
    builder.add_aggregation_type(DataProvider)

    # Add factories for `DataProvider` concretes.
    system_module.add_factories(
        mod_plugins.LetterDataProvider,
        mod_plugins.NumberDataProvider,
    )

    # This operation builds application instance.
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
    # - OptionalAllVariableFilter - filters only variables in __all__ (if present)
    # - DefinedVariableFilter - filters only variables with defined value
    # ---
    # By default option `export` in `add_values` is set,
    # so this value will be visible
    # when this module will be imported by another module.
    # add initialized config value
    config_module.scan_values(mod_config, VariableFilterSets.domain())

    # Lets create system module,
    # that will contain domain with connected concrete objects.
    system_module = builder.module_builder("system")
    # Add `config_module` to `system_module` imported modules.
    system_module.imports(config_module)
    # Add factory for `AllCombinations`.
    # ---
    # DI mechanism will try to call (create) this factory,
    # injecting non-abstract arguments matching type annotations.
    all_combinations_element = system_module.add_factory(mod_abstract.AllCombinations)

    # As an example mark argument named `providers` of `AllCombinations` factory (class)
    # to inject collection of object described in argument type annotation -
    # in this case `DataProvider` concrete objects.
    # ---
    # In previous test we marked `DataProvider` can be aggregated into collections
    # (if necessary) everywhere.
    # In this case aggregation of `DataProvider` concrete objects can be used
    # only in specified argument and specified factory case.
    builder.add_aggregation_spec(all_combinations_element, "providers")

    # Automatically add factories (classes) found in `mod_impl` and `mod_plugins`
    # python modules.
    # To filter only public concretes `FactoryFilterSets.domain()` filter cascade
    # is used.
    # `FactoryFilterSets.domain()` returns cascade, that contains:
    # - PublicFactoryFilter() - filters only public variables (by name)
    # - InternalsOrAllFactoryFilter() - filters only module internals
    #   or specified in __all__ module attribute
    # - NonAbstractFactoryFilter() - filters only concretes, skips abstract classes;
    #   by default duck typed abstract class check is used (raise NotImplementedError)
    system_module.scan_factories([mod_impl, mod_plugins], FactoryFilterSets.domain())

    # This operation builds application instance.
    instance = builder.build_instance()
    # This operation creates/gets `AllCombinations` provided
    # by automatic dependency injection mechanism.
    # ---
    # Particular value can be retrieved using some kind of pointer
    # returned by any `add_` operation like above.
    all_combinations = instance.value_of(all_combinations_element)

    # Check initialized application.
    _check_app_works(all_combinations)
