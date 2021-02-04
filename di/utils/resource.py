import re
from typing import Any, Optional, Tuple


class ResourceNameError(ValueError):
    pass


class ResourceName:
    feature_start = "@"
    module_pattern = r"^(?P<module>(?:[\w]+)(?:\.[\w]+)*)"
    name_sep = ":"
    name_pattern = r"(?P<name>[\w]+)"
    key_sep = "/"
    key_pattern = r"(?P<key>[\w]+)"
    module_name_re = re.compile(
        f"^{module_pattern}{re.escape(name_sep)}{name_pattern}$"
    )
    module_name_key_re = re.compile(
        f"^{module_pattern}{re.escape(name_sep)}{name_pattern}"
        f"{re.escape(key_sep)}{key_pattern}$"
    )

    @classmethod
    def for_feature(cls, name: str):
        return f"{cls.feature_start}{name}"

    @classmethod
    def for_name_key(cls, module: str, obj: str, key: str):
        return f"{cls.for_name(module, obj)}{cls.key_sep}{key}"

    @classmethod
    def for_name(cls, module: str, name: str):
        return f"{module}{cls.name_sep}{name}"

    @classmethod
    def parse_module_name(cls, rn: str) -> Tuple[str, str]:
        match = cls.module_name_re.match(rn)
        if match:
            return match.group("module"), match.group("name")
        else:
            raise ResourceNameError(f"Invalid module:name resource name: {rn}")

    @classmethod
    def parse_module_name_key(cls, rn: str) -> Tuple[str, str, str]:
        match = cls.module_name_key_re.match(rn)
        if match:
            return match.group("module"), match.group("name"), match.group("key")
        else:
            raise ResourceNameError(f"Invalid module:name/key resource name: {rn}")

    @classmethod
    def inspect_object_module(cls, obj) -> Optional[str]:
        return getattr(obj, "__module__", None)

    @classmethod
    def inspect_object_name(cls, obj) -> Optional[str]:
        return getattr(obj, "__name__", None)

    @classmethod
    def inspect_object(cls, obj) -> Optional[Tuple[str, str]]:
        if module := cls.inspect_object_module(obj):
            if name := cls.inspect_object_name(obj):
                return module, name
        return None


class Ref:
    _det: Tuple

    def rn(self) -> str:
        raise NotImplementedError

    def __hash__(self):
        return hash(self._det)

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return type(self) == type(other) and self._det == other._det


class _ModuleObjectRef(Ref):
    def __init__(self, module: str, name: str, obj: Optional[Any] = None):
        self._module = module
        self._name = name
        self._object = obj

    def rn(self) -> str:
        raise NotImplementedError

    @property
    def module(self):
        return self._module

    @property
    def name(self):
        return self._name

    @property
    def object(self):
        if not self._object:
            self._object = self.import_object(self._module, self._name)
        return self._object

    @classmethod
    def import_object(cls, module: str, name: str):
        module_obj = __import__(module)
        return getattr(module_obj, name)


class ModuleObjectRef(_ModuleObjectRef):
    def __init__(self, module: str, name: str, obj: Optional[Any] = None):
        super().__init__(module, name, obj)
        self._det = type(self), self._module, self._name

    @property
    def rn(self) -> str:
        return ResourceName.for_name(self._module, self._name)

    def sub(self, key: str):
        return ModuleObjectKeyRef(self._module, self._name, key, self._object)

    @classmethod
    def from_obj(cls, obj) -> Optional["ModuleObjectRef"]:
        if obj is not None:
            if module_name := ResourceName.inspect_object(obj):
                return ModuleObjectRef(*module_name, obj)
        return None

    @classmethod
    def from_rn(cls, rn: str):
        module, name = ResourceName.parse_module_name(rn)
        return ModuleObjectRef(module, name)

    def __repr__(self):
        return f"{type(self).__name__}<module={self._module}, object={self._object}>"

    def __str__(self):
        return ResourceName.for_name(self._module, self._name)


class ModuleObjectKeyRef(_ModuleObjectRef):
    def __init__(self, module: str, name: str, key: str, obj: Optional[Any] = None):
        super().__init__(module, name, obj)
        self._key = key
        self._det = type(self), self._module, self._name, self._key

    @property
    def key(self) -> str:
        return self._key

    def rn(self) -> str:
        return ResourceName.for_name_key(self._module, self._name, self._key)

    def parent(self):
        return ModuleObjectRef(self._module, self._name, self._object)

    @classmethod
    def from_obj(cls, obj, key: str) -> Optional["ModuleObjectKeyRef"]:
        if ref := ModuleObjectRef.from_obj(obj):
            return ref.sub(key)
        return None

    @classmethod
    def from_rn(cls, rn: str):
        module, name, key = ResourceName.parse_module_name_key(rn)
        return cls(module, name, key)

    def __repr__(self):
        return (
            f"{type(self).__name__}"
            f"<module={self._module}, name={self._name}>, key={self._key}>"
        )

    def __str__(self):
        return ResourceName.for_name_key(self._module, self._name, self._key)


class FeatureRef(Ref):
    def __init__(self, feature: str):
        self._feature = feature
        self._det = type(self), self._feature

    def rn(self) -> str:
        return ResourceName.for_feature(self._feature)

    @property
    def feature(self):
        return self._feature

    def __repr__(self):
        return f"{type(self).__name__}<feature={self._feature}>"

    def __str__(self):
        return self._feature
