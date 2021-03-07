"""
Main module of small application, that generates all combinations
for string collection - composite of elements returned by various data providers.
"""

from typing import Collection, FrozenSet, List

from tests.di.declarative.mod_config import Config


class GroupCombinationsGenerator:
    """
    Combination generation algorithm interface (contract)
    """

    def generate(self, data: Collection[str], num: int) -> Collection[FrozenSet[str]]:
        raise NotImplementedError


class DataProvider:
    """
    Data provider interface (contract)
    """

    def all(self) -> Collection[str]:
        raise NotImplementedError


class AllCombinations:
    """
    All combinations generator - example domain object
    """

    def __init__(
        self,
        config: Config,
        combinations_generator: GroupCombinationsGenerator,
        providers: List[DataProvider],
    ):
        """
        All combination generation init
        :param config: generator config
        :param combinations_generator: generator algorithm
        :param providers: data providers
        """
        self.config = config
        self.combinations_generator = combinations_generator
        self.providers = providers

    def all(self) -> Collection[FrozenSet[str]]:
        """
        Domain operation of combination generation
        :return: all combinations
        """
        all_data = {e for provider in self.providers for e in provider.all()}
        return self.combinations_generator.generate(all_data, self.config.num)
