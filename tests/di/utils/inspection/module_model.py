from dataclasses import dataclass


class NormalClass:
    pass


class ExtendedNormalClass(NormalClass):
    pass


@dataclass
class DataClass:
    name: str
