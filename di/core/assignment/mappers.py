from typing import Callable, Collection, Iterable, Sequence

from di.core.assignment.base import ValuesMapper


class SingleValuesMapper(ValuesMapper):
    def map(self, objects: Sequence):
        assert len(objects) == 1, "Invalid objects sequence"
        return objects[0]


class MixedIterableValuesMapper(ValuesMapper):
    def __init__(
        self,
        container_factory: Callable[[Iterable], Collection],
        iterate_args: Sequence[bool],
    ):
        self.container_factory = container_factory
        self.iterate_args = iterate_args

    def map(self, objects: Sequence):
        return self.container_factory(self._iterate(objects))

    def _iterate(self, objects: Sequence) -> Iterable:
        assert len(objects) == len(self.iterate_args), "Invalid objects sequence"
        for obj, iterate_arg in zip(objects, self.iterate_args):
            if iterate_arg:
                yield from obj
            else:
                yield obj
