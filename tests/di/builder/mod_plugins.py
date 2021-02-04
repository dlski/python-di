from typing import Collection

from tests.di.builder.mod_abstract import DataProvider


class LetterDataProvider(DataProvider):
    def all(self) -> Collection[str]:
        return list("AB")


class NumberDataProvider(DataProvider):
    def all(self) -> Collection[str]:
        return list("12")
