import unittest

from push_relabel.base import PushRelabel
from test_base_against_reference import (
    SEEDS,
    SCENARIOS,
    edmonds_karp,
    generate_graph,
)


class CountingGapPushRelabel(PushRelabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gap_calls = 0
        self.test_seed = None
        self.test_scenario = None
        self.test_edges = None
        self.test_source = None
        self.test_sink = None

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
        if self.gap_calls > 1000:
            raise AssertionError(
                "gap relabel call limit exceeded: "
                f"seed={self.test_seed}, scenario={self.test_scenario}, "
                f"number_of_vertices={self.n}, "
                f"source={self.test_source}, sink={self.test_sink}, "
                f"edges={self.test_edges}, gap_calls={self.gap_calls}"
            )
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


def build_gap_push_relabel(
    number_of_vertices,
    edges,
    seed,
    scenario,
    source,
    sink,
):
    push_relabel = CountingGapPushRelabel(
        number_of_vertices,
        use_global=False,
        use_gap=True,
    )
    push_relabel.test_seed = seed
    push_relabel.test_scenario = scenario
    push_relabel.test_edges = edges
    push_relabel.test_source = source
    push_relabel.test_sink = sink

    for from_vertex, to_vertex, capacity in edges:
        push_relabel.add_edge(from_vertex, to_vertex, capacity)

    return push_relabel


class TestGapRelabelAgainstReference(unittest.TestCase):
    def test_all_reference_graphs_match_edmonds_karp(self):
        self.assertEqual(len(SEEDS), 70)

        for index, seed in enumerate(SEEDS):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            number_of_vertices, edges, source, sink = generate_graph(seed, scenario)
            expected = edmonds_karp(
                number_of_vertices,
                edges,
                source,
                sink,
            )
            push_relabel = build_gap_push_relabel(
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
                f"gap_relabel={actual}, edmonds_karp={expected}, "
                f"gap_calls={push_relabel.gap_calls}"
            )
            self.assertEqual(actual, expected, message)

    def test_gap_relabel_is_invoked(self):
        seed = 1000
        scenario = SCENARIOS[0]
        number_of_vertices, edges, source, sink = generate_graph(seed, scenario)
        expected = edmonds_karp(number_of_vertices, edges, source, sink)
        push_relabel = build_gap_push_relabel(
            number_of_vertices,
            edges,
            seed,
            scenario,
            source,
            sink,
        )
        actual = push_relabel.max_flow(source, sink)

        self.assertEqual(actual, expected)
        self.assertGreater(push_relabel.gap_calls, 0)


if __name__ == "__main__":
    unittest.main()
