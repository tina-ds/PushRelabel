import unittest

from push_relabel.base import compute_max_flow


class TestBaseCorrectness(unittest.TestCase):
    def test_known_graph_has_maximum_flow_five(self):
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

        self.assertEqual(
            compute_max_flow(number_of_vertices, edges, source, sink),
            5,
        )

    def test_graph_without_source_to_sink_path_has_zero_flow(self):
        number_of_vertices = 4
        source = 0
        sink = 3
        edges = [
            (0, 1, 4),
            (2, 3, 5),
        ]

        self.assertEqual(
            compute_max_flow(number_of_vertices, edges, source, sink),
            0,
        )

    def test_edge_entering_source_is_not_counted_as_flow(self):
        number_of_vertices = 4
        source = 0
        sink = 3
        edges = [
            (2, 0, 7),
            (0, 1, 5),
            (1, 3, 5),
        ]

        self.assertEqual(
            compute_max_flow(number_of_vertices, edges, source, sink),
            5,
        )

    def test_multiple_edges_entering_source_are_not_counted_as_flow(self):
        number_of_vertices = 5
        source = 0
        sink = 4
        edges = [
            (2, 0, 7),
            (3, 0, 11),
            (0, 1, 6),
            (1, 4, 6),
        ]

        self.assertEqual(
            compute_max_flow(number_of_vertices, edges, source, sink),
            6,
        )

    def test_input_edges_remain_unchanged(self):
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
        original_edges = edges.copy()

        compute_max_flow(number_of_vertices, edges, source, sink)

        self.assertEqual(edges, original_edges)


if __name__ == "__main__":
    unittest.main()
