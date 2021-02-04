from di.core.element import Element


class ApplicationInstanceStateError(AssertionError):
    pass


class ApplicationInstanceError(Exception):
    pass


class ApplicationInstanceElementNotFound(ApplicationInstanceError):
    def __init__(self, element: Element):
        super().__init__(f"Element {element} not found")
        self.element = element


class ApplicationInstance:
    def value_of(self, element: Element):
        raise NotImplementedError


class ApplicationInstanceBuilder:
    def build(self) -> ApplicationInstance:
        raise NotImplementedError
