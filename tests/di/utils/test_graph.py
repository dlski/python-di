from typing import List

import pytest

from di.utils.graph import (
    DirectionalGraph,
    DirectionalGraphEdge,
    DirectionalGraphIteratorError,
    DirectionalGraphTopologyIterator,
)


@pytest.fixture
def elements():
    return [1, 2, 3, 4]


class IntGraphEdge(DirectionalGraphEdge[int]):
    __slots__ = "source", "target"

    def __init__(self, source: int, target: int):
        self.source = source
        self.target = target


@pytest.fixture
def edges():
    return [
        IntGraphEdge(1, 2),
        IntGraphEdge(1, 3),
        IntGraphEdge(1, 4),
        IntGraphEdge(2, 3),
        IntGraphEdge(2, 4),
        IntGraphEdge(3, 4),
    ]


@pytest.fixture
def cycle_edges():
    return [
        IntGraphEdge(1, 4),
        IntGraphEdge(2, 3),
        IntGraphEdge(3, 2),
        IntGraphEdge(3, 4),
    ]


def test_graph(elements: List[int], edges: List[IntGraphEdge]):
    graph = DirectionalGraph(elements, edges)
    stages = list(DirectionalGraphTopologyIterator(graph))
    assert len(stages) == 4
    assert 4 in stages[0]
    assert 3 in stages[1]
    assert 2 in stages[2]
    assert 1 in stages[3]


def test_graph_with_cycle(elements: List[int], cycle_edges: List[IntGraphEdge]):
    graph = DirectionalGraph(elements, cycle_edges)
    with pytest.raises(DirectionalGraphIteratorError):
        list(DirectionalGraphTopologyIterator(graph))
