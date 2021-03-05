import sys

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    _undefined = object()

    # noinspection PyPep8Naming
    class cached_property:
        def __init__(self, func):
            self.func = func
            self.attr_name = None
            self.__doc__ = func.__doc__

        def __set_name__(self, owner, name):
            if self.attr_name is None:
                self.attr_name = name
            elif name != self.attr_name:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    f"({self.attr_name!r} and {name!r})."
                )

        def __get__(self, instance, owner=None):
            if instance is None:
                return self

            cache = instance.__dict__
            name = self.attr_name

            value = cache.get(name, _undefined)
            if value is _undefined:
                value = cache[name] = self.func(instance)
            return value


__all__ = [
    "cached_property",
]
