from di.builder.app import AppBuilder
from di.builder.filters import FactoryFilterSets, VariableFilterSets
from tests.di.builder import mod_abstract, mod_config, mod_impl, mod_plugins
from tests.di.builder.mod_abstract import AllCombinations, DataProvider


def _check_app_works(all_combinations: AllCombinations):
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


def test_builder_manual():
    builder = AppBuilder(aggregation_types=[DataProvider])
    # config
    config_module = builder.module_builder("config")
    config_module.add_values(mod_config.config)
    # system
    system_module = builder.module_builder("system")
    system_module.imports(config_module)
    all_combinations_element = system_module.add_factory(mod_abstract.AllCombinations)
    system_module.add_factory(mod_impl.ItertoolsPairCombinationsGenerator)
    system_module.add_factories(
        mod_plugins.LetterDataProvider,
        mod_plugins.NumberDataProvider,
    )

    instance = builder.build_instance()
    _check_app_works(instance.value_of(all_combinations_element))


def test_builder_scan():
    builder = AppBuilder()
    # config
    config_module = builder.module_builder("config")
    config_module.scan_values(mod_config, VariableFilterSets.domain())
    # system
    system_module = builder.module_builder("system")
    system_module.imports(config_module)
    all_combinations_element = system_module.add_factory(mod_abstract.AllCombinations)
    builder.add_aggregation_spec(all_combinations_element, "providers")
    system_module.scan_factories([mod_impl, mod_plugins], FactoryFilterSets.domain())

    instance = builder.build_instance()
    _check_app_works(instance.value_of(all_combinations_element))
