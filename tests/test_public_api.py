import unittest

import push_relabel
from push_relabel import PushRelabelHighest
from push_relabel.highest import PushRelabelHighest as HighestImplementation


class TestPublicAPI(unittest.TestCase):
    def test_highest_label_export(self):
        expected_exports = [
            "Edge",
            "PushRelabel",
            "PushRelabelHighest",
            "compute_max_flow",
        ]

        self.assertIs(PushRelabelHighest, HighestImplementation)
        self.assertIn("PushRelabelHighest", push_relabel.__all__)
        self.assertIn("Edge", push_relabel.__all__)
        self.assertIn("PushRelabel", push_relabel.__all__)
        self.assertIn("compute_max_flow", push_relabel.__all__)
        self.assertEqual(len(push_relabel.__all__), len(set(push_relabel.__all__)))
        self.assertEqual(push_relabel.__all__, expected_exports)


if __name__ == "__main__":
    unittest.main()
