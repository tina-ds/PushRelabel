import random
import unittest
from collections import deque

from push_relabel.base import compute_max_flow


SEEDS = tuple(range(1000, 1070))
SCENARIOS = (
    "general",
    "cycle",
    "incoming_source",
    "outgoing_sink",
    "antiparallel",
    "no_path",
    "parallel_routes",
)


def edmonds_karp(number_of_vertices, edges, source, sink):
    residual = [[0] * number_of_vertices for _ in range(number_of_vertices)]
    adjacency = [set() for _ in range(number_of_vertices)]

    for from_vertex, to_vertex, capacity in edges:
        residual[from_vertex][to_vertex] += capacity
        adjacency[from_vertex].add(to_vertex)
        adjacency[to_vertex].add(from_vertex)

    maximum_flow = 0

    while True:
        parent = [-1] * number_of_vertices
        parent[source] = source
        queue = deque([source])

        while queue and parent[sink] == -1:
            vertex = queue.popleft()
            for neighbor in sorted(adjacency[vertex]):
                if parent[neighbor] == -1 and residual[vertex][neighbor] > 0:
                    parent[neighbor] = vertex
                    queue.append(neighbor)
                    if neighbor == sink:
                        break

        if parent[sink] == -1:
            return maximum_flow

        path_capacity = float("inf")
        vertex = sink
        while vertex != source:
            previous = parent[vertex]
            path_capacity = min(path_capacity, residual[previous][vertex])
            vertex = previous

        vertex = sink
        while vertex != source:
            previous = parent[vertex]
            residual[previous][vertex] -= path_capacity
            residual[vertex][previous] += path_capacity
            vertex = previous

        maximum_flow += path_capacity


def generate_graph(seed, scenario):
    random_generator = random.Random(seed)
    number_of_vertices = random_generator.randint(2, 10)

    if scenario in {
        "cycle",
        "incoming_source",
        "outgoing_sink",
        "antiparallel",
    }:
        number_of_vertices = max(number_of_vertices, 3)
    elif scenario == "parallel_routes":
        number_of_vertices = max(number_of_vertices, 4)

    source = 0
    sink = number_of_vertices - 1
    edge_capacities = {}

    def add_edge(from_vertex, to_vertex):
        pair = (from_vertex, to_vertex)
        if from_vertex != to_vertex and pair not in edge_capacities:
            edge_capacities[pair] = random_generator.randint(1, 20)

    if scenario == "cycle":
        add_edge(0, 1)
        add_edge(1, 2)
        add_edge(2, 0)
    elif scenario == "incoming_source":
        add_edge(1, source)
        add_edge(source, 1)
        add_edge(1, sink)
    elif scenario == "outgoing_sink":
        add_edge(source, 1)
        add_edge(1, sink)
        add_edge(sink, 1)
    elif scenario == "antiparallel":
        add_edge(source, 1)
        add_edge(1, source)
        add_edge(1, sink)
    elif scenario == "parallel_routes":
        add_edge(source, 1)
        add_edge(1, sink)
        add_edge(source, 2)
        add_edge(2, sink)

    for from_vertex in range(number_of_vertices):
        for to_vertex in range(number_of_vertices):
            if from_vertex == to_vertex:
                continue
            if scenario == "no_path" and from_vertex == source:
                continue
            if random_generator.random() < 0.22:
                add_edge(from_vertex, to_vertex)

    edges = [
        (from_vertex, to_vertex, edge_capacities[(from_vertex, to_vertex)])
        for from_vertex, to_vertex in sorted(edge_capacities)
    ]
    return number_of_vertices, edges, source, sink


class TestBaseAgainstReference(unittest.TestCase):
    def test_deterministic_random_graphs_match_edmonds_karp(self):
        for index, seed in enumerate(SEEDS):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            number_of_vertices, edges, source, sink = generate_graph(seed, scenario)

            expected = edmonds_karp(
                number_of_vertices,
                edges,
                source,
                sink,
            )
            actual = compute_max_flow(
                number_of_vertices,
                edges,
                source,
                sink,
            )

            message = (
                f"seed={seed}, scenario={scenario}, "
                f"number_of_vertices={number_of_vertices}, "
                f"source={source}, sink={sink}, edges={edges}, "
                f"compute_max_flow={actual}, edmonds_karp={expected}"
            )
            self.assertEqual(actual, expected, message)


if __name__ == "__main__":
    unittest.main()
