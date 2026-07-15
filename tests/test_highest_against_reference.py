import unittest

from push_relabel.highest import PushRelabelHighest
from test_base_against_reference import (
    SEEDS,
    SCENARIOS,
    edmonds_karp,
    generate_graph,
)


class CountingHighestPushRelabel(PushRelabelHighest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_calls = 0
        self.relabel_calls = 0
        self.test_seed = None
        self.test_scenario = None
        self.test_edges = None
        self.test_source = None
        self.test_sink = None

    def _assert_call_limit(self):
        if self.push_calls + self.relabel_calls > 100000:
            raise AssertionError(
                "highest-label call limit exceeded: "
                f"seed={self.test_seed}, scenario={self.test_scenario}, "
                f"number_of_vertices={self.n}, "
                f"source={self.test_source}, sink={self.test_sink}, "
                f"edges={self.test_edges}, push_calls={self.push_calls}, "
                f"relabel_calls={self.relabel_calls}"
            )

    def _push(
        self,
        u,
        e,
        excess,
        height,
        is_active,
        buckets,
        current_max_h,
        source,
        sink,
    ):
        self.push_calls += 1
        self._assert_call_limit()
        return super()._push(
            u,
            e,
            excess,
            height,
            is_active,
            buckets,
            current_max_h,
            source,
            sink,
        )

    def _relabel(self, u, height):
        self.relabel_calls += 1
        self._assert_call_limit()
        return super()._relabel(u, height)


def build_highest_push_relabel(
    number_of_vertices,
    edges,
    seed,
    scenario,
    source,
    sink,
):
    push_relabel = CountingHighestPushRelabel(number_of_vertices)
    push_relabel.test_seed = seed
    push_relabel.test_scenario = scenario
    push_relabel.test_edges = edges
    push_relabel.test_source = source
    push_relabel.test_sink = sink

    for from_vertex, to_vertex, capacity in edges:
        push_relabel.add_edge(from_vertex, to_vertex, capacity)

    return push_relabel


class TestHighestAgainstReference(unittest.TestCase):
    def test_all_reference_graphs_match_edmonds_karp(self):
        self.assertEqual(SEEDS, tuple(range(1000, 1070)))

        for index, seed in enumerate(SEEDS):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            number_of_vertices, edges, source, sink = generate_graph(seed, scenario)
            expected = edmonds_karp(
                number_of_vertices,
                edges,
                source,
                sink,
            )
            push_relabel = build_highest_push_relabel(
                number_of_vertices,
                edges,
                seed,
                scenario,
                source,
                sink,
            )
            actual = push_relabel.max_flow(source, sink)

            message = (
                f"seed={seed}, scenario={scenario}, "
                f"number_of_vertices={number_of_vertices}, "
                f"source={source}, sink={sink}, edges={edges}, "
                f"highest_label={actual}, edmonds_karp={expected}, "
                f"push_calls={push_relabel.push_calls}, "
                f"relabel_calls={push_relabel.relabel_calls}"
            )
            self.assertEqual(actual, expected, message)

    def test_edge_entering_source_is_not_counted_as_flow(self):
        number_of_vertices = 4
        source = 0
        sink = 3
        edges = [
            (2, 0, 7),
            (0, 1, 5),
            (1, 3, 5),
        ]
        push_relabel = build_highest_push_relabel(
            number_of_vertices,
            edges,
            "incoming_source_regression",
            "incoming_source",
            source,
            sink,
        )

        self.assertEqual(push_relabel.max_flow(source, sink), 5)

    def test_push_and_relabel_are_invoked(self):
        number_of_vertices = 4
        source = 0
        sink = 3
        edges = [
            (0, 1, 3),
            (0, 2, 2),
            (1, 2, 1),
            (1, 3, 2),
            (2, 3, 3),
        ]
        push_relabel = build_highest_push_relabel(
            number_of_vertices,
            edges,
            "invocation_probe",
            "known_graph",
            source,
            sink,
        )
        actual = push_relabel.max_flow(source, sink)
        expected = edmonds_karp(number_of_vertices, edges, source, sink)

        self.assertEqual(actual, expected)
        self.assertGreater(push_relabel.push_calls, 0)
        self.assertGreater(push_relabel.relabel_calls, 0)


if __name__ == "__main__":
    unittest.main()
