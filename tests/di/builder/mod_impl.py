"""
Module containing concrete implementation of `GroupCombinationsGenerator`
"""

import itertools
from typing import Collection, FrozenSet

from tests.di.builder.mod_abstract import GroupCombinationsGenerator


class ItertoolsGroupCombinationsGenerator(GroupCombinationsGenerator):
    """
    Concrete implementation of combinations generator
    """

    def generate(self, data: Collection[str], num: int) -> Collection[FrozenSet[str]]:
        return [frozenset(comb) for comb in itertools.combinations(data, num)]
