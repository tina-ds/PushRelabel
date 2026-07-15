import unittest

from push_relabel.base import PushRelabel
from test_base_against_reference import (
    SEEDS,
    SCENARIOS,
    edmonds_karp,
    generate_graph,
)


class CountingGlobalGapPushRelabel(PushRelabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.global_relabel_calls = 0
        self.gap_calls = 0
        self.test_seed = None
        self.test_scenario = None
        self.test_edges = None
        self.test_source = None
        self.test_sink = None

    def _assert_call_limits(self):
        if self.global_relabel_calls > 1000 or self.gap_calls > 1000:
            raise AssertionError(
                "heuristic call limit exceeded: "
                f"seed={self.test_seed}, scenario={self.test_scenario}, "
                f"number_of_vertices={self.n}, "
                f"source={self.test_source}, sink={self.test_sink}, "
                f"edges={self.test_edges}, "
                f"global_relabel_calls={self.global_relabel_calls}, "
                f"gap_calls={self.gap_calls}"
            )

    def _global_relabel(
        self,
        s,
        t,
        height,
        excess,
        active,
        in_queue,
        count,
    ):
        self.global_relabel_calls += 1
        self._assert_call_limits()
        return super()._global_relabel(
            s,
            t,
            height,
            excess,
            active,
            in_queue,
            count,
        )

    def _gap(
        self,
        k,
        height,
        count,
        excess,
        active,
        in_queue,
        s,
        t,
    ):
        self.gap_calls += 1
        self._assert_call_limits()
        return super()._gap(
            k,
            height,
            count,
            excess,
            active,
            in_queue,
            s,
            t,
        )


def build_global_gap_push_relabel(
    number_of_vertices,
    edges,
    seed,
    scenario,
    source,
    sink,
):
    push_relabel = CountingGlobalGapPushRelabel(
        number_of_vertices,
        use_global=True,
        use_gap=True,
        global_freq=1,
    )
    push_relabel.test_seed = seed
    push_relabel.test_scenario = scenario
    push_relabel.test_edges = edges
    push_relabel.test_source = source
    push_relabel.test_sink = sink

    for from_vertex, to_vertex, capacity in edges:
        push_relabel.add_edge(from_vertex, to_vertex, capacity)

    return push_relabel


class TestGlobalGapAgainstReference(unittest.TestCase):
    def test_all_reference_graphs_match_edmonds_karp(self):
        self.assertEqual(SEEDS, tuple(range(1000, 1070)))
        global_call_counts = []
        gap_call_counts = []

        for index, seed in enumerate(SEEDS):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            number_of_vertices, edges, source, sink = generate_graph(seed, scenario)
            expected = edmonds_karp(
                number_of_vertices,
                edges,
                source,
                sink,
            )
            push_relabel = build_global_gap_push_relabel(
                number_of_vertices,
                edges,
                seed,
                scenario,
                source,
                sink,
            )
            actual = push_relabel.max_flow(source, sink)
            global_call_counts.append(push_relabel.global_relabel_calls)
            gap_call_counts.append(push_relabel.gap_calls)

            message = (
                f"seed={seed}, scenario={scenario}, "
                f"number_of_vertices={number_of_vertices}, "
                f"source={source}, sink={sink}, edges={edges}, "
                f"global_gap={actual}, edmonds_karp={expected}, "
                f"global_relabel_calls={push_relabel.global_relabel_calls}, "
                f"gap_calls={push_relabel.gap_calls}"
            )
            self.assertEqual(actual, expected, message)

        self.assertGreater(sum(count > 0 for count in global_call_counts), 0)
        self.assertGreater(sum(count > 0 for count in gap_call_counts), 0)

    def test_known_counterexamples(self):
        cases = (
            (1000, "general", 15),
            (1003, "outgoing_sink", 17),
        )

        for seed, scenario, expected in cases:
            number_of_vertices, edges, source, sink = generate_graph(seed, scenario)
            reference = edmonds_karp(
                number_of_vertices,
                edges,
                source,
                sink,
            )
            push_relabel = build_global_gap_push_relabel(
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
                f"global_gap={actual}, edmonds_karp={reference}, "
                f"expected={expected}, "
                f"global_relabel_calls={push_relabel.global_relabel_calls}, "
                f"gap_calls={push_relabel.gap_calls}"
            )
            self.assertEqual(reference, expected, message)
            self.assertEqual(actual, expected, message)


if __name__ == "__main__":
    unittest.main()
