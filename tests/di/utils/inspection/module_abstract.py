from abc import ABC, abstractmethod
from typing import Type


class NormalClass:
    def test(self) -> Type[Exception]:
        # raise NotImplementedError
        return NotImplementedError


class CanonicalAbstract(ABC):
    @abstractmethod
    def abstract(self):
        pass


class DuckAbstract1:
    def test(self):
        raise NotImplementedError


class DuckAbstract2:
    def test(self):
        raise NotImplementedError(f"Method is not implemented in {self}")


class DuckAbstract3:
    @classmethod
    async def test(cls):
        raise NotImplementedError(f"Async method not implemented in {cls}")


class DuckAbstract4:
    @staticmethod
    def test():
        raise NotImplementedError("Static method is not implemented")


class DuckAbstract5:
    @property
    def test_property(self):
        raise NotImplementedError(f"Property is not implemented in {self}")


class ImplementedAbstracts(DuckAbstract1, DuckAbstract5):
    def test(self):
        pass

    @property
    def test_property(self):
        return None


def normal_fn():
    return NotImplementedError


def abstract_fn():
    raise NotImplementedError(f"Function is not implemented in {__name__}")


async def normal_async_fn():
    return NotImplementedError


async def abstract_async_fn():
    raise NotImplementedError(f"Async function is not implemented in {__name__}")
