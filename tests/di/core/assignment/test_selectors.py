from di.core.assignment.factories import DirectAssignmentFactory
from di.core.assignment.selectors import DirectAssignmentFactorySelector


def test_direct_assignment_factory_selector():
    selector = DirectAssignmentFactorySelector()
    factory = selector.select(...)
    assert isinstance(factory, DirectAssignmentFactory)
