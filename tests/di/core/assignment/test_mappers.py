from di.core.assignment import MixedIterableValuesMapper, SingleValuesMapper


def test_single_values_mapper():
    objects = ["test"]
    mapper = SingleValuesMapper()
    assert mapper.map(objects) == objects[0]


def test_aggregation_values_mapper():
    objects = [{1, 2, 3}, 1.0, ["a", "b", "c"], True, False]
    superset = set()
    for obj in objects:
        if isinstance(obj, (set, list)):
            superset.update(obj)
        else:
            superset.add(obj)

    mapper = MixedIterableValuesMapper(
        container_factory=set,
        iterate_args=[isinstance(obj, (set, list)) for obj in objects],
    )
    result = mapper.map(objects)
    assert result
    assert isinstance(result, set)
    assert result == superset

    mapper.container_factory = list
    result = mapper.map(objects)
    assert result
    assert isinstance(result, list)
    assert all(item in superset for item in result)
    assert all(item in result for item in superset)
