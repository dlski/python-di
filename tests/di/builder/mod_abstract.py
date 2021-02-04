from typing import Collection, FrozenSet, List

from tests.di.builder.mod_config import Config


class PairCombinationsGenerator:
    def generate(self, data: Collection[str], num: int) -> Collection[FrozenSet[str]]:
        raise NotImplementedError


class DataProvider:
    def all(self) -> Collection[str]:
        raise NotImplementedError


class AllCombinations:
    def __init__(
        self,
        config: Config,
        combinations_generator: PairCombinationsGenerator,
        providers: List[DataProvider],
    ):
        self.config = config
        self.combinations_generator = combinations_generator
        self.providers = providers

    def all(self) -> Collection[FrozenSet[str]]:
        all_data = {e for provider in self.providers for e in provider.all()}
        return self.combinations_generator.generate(all_data, self.config.num)
