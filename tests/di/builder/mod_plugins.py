"""
Module containing implementations of concrete data providers
"""

from typing import Collection

from tests.di.builder.mod_abstract import DataProvider


class LetterDataProvider(DataProvider):
    """
    Concrete data provider returning collection containing "A" and "B"
    """

    def all(self) -> Collection[str]:
        return list("AB")


class NumberDataProvider(DataProvider):
    """
    Concrete data provider returning collection containing "1" and "2"
    """

    def all(self) -> Collection[str]:
        return list("12")
