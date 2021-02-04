import itertools
from typing import Collection, FrozenSet

from tests.di.builder.mod_abstract import PairCombinationsGenerator


class ItertoolsPairCombinationsGenerator(PairCombinationsGenerator):
    def generate(self, data: Collection[str], num: int) -> Collection[FrozenSet[str]]:
        return [frozenset(comb) for comb in itertools.combinations(data, num)]
