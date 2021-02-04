from typing import Dict, Generic, Iterable, Set, TypeVar

GraphNodeType = TypeVar("GraphNodeType")


class DirectionalGraphEdge(Generic[GraphNodeType]):
    __slots__ = ()

    source: GraphNodeType
    target: GraphNodeType

    def __hash__(self):
        return hash((self.source, self.target))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.source == other.source and self.target == other.target
        return False


GraphEdgeType = TypeVar("GraphEdgeType", bound=DirectionalGraphEdge)


class DirectionalGraph(Generic[GraphNodeType, GraphEdgeType]):
    __slots__ = "nodes", "edges"

    def __init__(self, nodes: Iterable[GraphNodeType], edges: Iterable[GraphEdgeType]):
        self.nodes = list(set(nodes))
        self.edges = list(set(edges))

    def source_targets(self) -> Dict[GraphNodeType, Set[GraphNodeType]]:
        _map = {node: set() for node in self.nodes}
        for edge in self.edges:
            _map[edge.source].add(edge.target)
        return _map

    def target_sources(self) -> Dict[GraphNodeType, Set[GraphNodeType]]:
        _map = {node: set() for node in self.nodes}
        for edge in self.edges:
            _map[edge.target].add(edge.source)
        return _map


class DirectionalGraphIteratorError(Exception):
    pass


class DirectionalGraphTopologyIterator(Generic[GraphNodeType, GraphEdgeType]):
    __slots__ = "source_targets", "visited", "to_visit"

    def __init__(self, graph: DirectionalGraph[GraphNodeType, GraphEdgeType]):
        self.source_targets = graph.source_targets()
        self.visited = set()
        self.to_visit = set(graph.nodes)

    def __iter__(self):
        return self

    def __next__(self) -> Set[GraphNodeType]:
        if not self.to_visit:
            raise StopIteration
        step = set()
        for node in self.to_visit:
            if self.source_targets[node].issubset(self.visited):
                step.add(node)
        if not step:
            raise DirectionalGraphIteratorError("Cyclic connection in graph")
        self.visited.update(step)
        self.to_visit.difference_update(step)
        return step
