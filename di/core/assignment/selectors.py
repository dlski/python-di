from di.core.assignment.base import AssignmentFactory, AssignmentFactorySelector
from di.core.assignment.factories import DirectAssignmentFactory
from di.core.element import Dependency


class DirectAssignmentFactorySelector(AssignmentFactorySelector):
    def __init__(self):
        self._factory = DirectAssignmentFactory()

    def select(self, dependency: Dependency) -> AssignmentFactory:
        return self._factory
