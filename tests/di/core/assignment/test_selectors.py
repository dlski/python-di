from di.core.assignment import DirectAssignmentFactory, DirectAssignmentFactorySelector


def test_direct_assignment_factory_selector():
    selector = DirectAssignmentFactorySelector()
    factory = selector.select(...)
    assert isinstance(factory, DirectAssignmentFactory)
