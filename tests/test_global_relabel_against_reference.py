import unittest

from push_relabel.base import PushRelabel
from test_base_against_reference import SEEDS, edmonds_karp, generate_graph


SCENARIOS = (
    "general",
    "cycle",
    "incoming_source",
    "outgoing_sink",
    "antiparallel",
    "no_path",
    "parallel_routes",
)


class CountingGlobalPushRelabel(PushRelabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.global_relabel_calls = 0
        self.test_seed = None
        self.test_edges = None
        self.test_source = None
        self.test_sink = None

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
        if self.global_relabel_calls > 1000:
            raise AssertionError(
                "global relabel call limit exceeded: "
                f"seed={self.test_seed}, "
                f"number_of_vertices={self.n}, "
                f"source={self.test_source}, sink={self.test_sink}, "
                f"edges={self.test_edges}, "
                f"global_relabel_calls={self.global_relabel_calls}"
            )
        return super()._global_relabel(
            s,
            t,
            height,
            excess,
            active,
            in_queue,
            count,
        )


def build_global_push_relabel(
    push_relabel_class,
    number_of_vertices,
    edges,
    seed,
    source,
    sink,
):
    push_relabel = push_relabel_class(
        number_of_vertices,
        use_global=True,
        use_gap=False,
        global_freq=1,
    )
    if isinstance(push_relabel, CountingGlobalPushRelabel):
        push_relabel.test_seed = seed
        push_relabel.test_edges = edges
        push_relabel.test_source = source
        push_relabel.test_sink = sink
    for from_vertex, to_vertex, capacity in edges:
        push_relabel.add_edge(from_vertex, to_vertex, capacity)
    return push_relabel


class TestGlobalRelabelAgainstReference(unittest.TestCase):
    def test_all_reference_graphs_match_edmonds_karp(self):
        self.assertEqual(len(SEEDS), 70)
        call_counts = []

        for index, seed in enumerate(SEEDS):
            scenario = SCENARIOS[index % len(SCENARIOS)]
            number_of_vertices, edges, source, sink = generate_graph(seed, scenario)

            expected = edmonds_karp(
                number_of_vertices,
                edges,
                source,
                sink,
            )
            push_relabel = build_global_push_relabel(
                CountingGlobalPushRelabel,
                number_of_vertices,
                edges,
                seed,
                source,
                sink,
            )
            actual = push_relabel.max_flow(source, sink)
            call_counts.append(push_relabel.global_relabel_calls)

            message = (
                f"seed={seed}, scenario={scenario}, "
                f"number_of_vertices={number_of_vertices}, "
                f"source={source}, sink={sink}, edges={edges}, "
                f"global_relabel={actual}, edmonds_karp={expected}"
            )
            self.assertEqual(actual, expected, message)
            if seed == 1000:
                self.assertEqual(actual, 15, message)

        self.assertLessEqual(max(call_counts), 1000)

    def test_known_nontermination_counterexamples(self):
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
            push_relabel = build_global_push_relabel(
                CountingGlobalPushRelabel,
                number_of_vertices,
                edges,
                seed,
                source,
                sink,
            )
            actual = push_relabel.max_flow(source, sink)

            message = (
                f"seed={seed}, scenario={scenario}, "
                f"number_of_vertices={number_of_vertices}, "
                f"source={source}, sink={sink}, edges={edges}, "
                f"global_relabel={actual}, edmonds_karp={reference}, "
                f"expected={expected}"
            )
            self.assertEqual(reference, expected, message)
            self.assertEqual(actual, expected, message)

    def test_global_relabel_is_invoked_with_frequency_one(self):
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

        push_relabel = build_global_push_relabel(
            CountingGlobalPushRelabel,
            number_of_vertices,
            edges,
            "invocation_probe",
            source,
            sink,
        )
        actual = push_relabel.max_flow(source, sink)
        expected = edmonds_karp(number_of_vertices, edges, source, sink)

        self.assertEqual(actual, expected)
        self.assertGreater(push_relabel.global_relabel_calls, 0)


if __name__ == "__main__":
    unittest.main()
