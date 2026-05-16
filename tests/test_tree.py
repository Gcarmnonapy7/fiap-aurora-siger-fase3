"""Tests for the Node class (N-ary tree)."""

import unittest

from colony.tree import Node


class TestNodeStructure(unittest.TestCase):

    def test_leaf_node_carries_module(self):
        n = Node("Solar", module={"id": 4})
        self.assertEqual(n.name, "Solar")
        self.assertEqual(n.module, {"id": 4})
        self.assertEqual(n.children, [])

    def test_internal_node_has_no_module(self):
        n = Node("Energy")
        self.assertIsNone(n.module)
        self.assertEqual(n.children, [])

    def test_add_child(self):
        root = Node("Energy")
        leaf = Node("Solar", module={"id": 4})
        root.add_child(leaf)
        self.assertEqual(len(root.children), 1)
        self.assertIs(root.children[0], leaf)

    def test_is_leaf(self):
        root = Node("Energy")
        leaf = Node("Solar", module={"id": 4})
        root.add_child(leaf)
        self.assertFalse(root.is_leaf())
        self.assertTrue(leaf.is_leaf())


class TestNodeTraversals(unittest.TestCase):

    def _sample_tree(self):
        # Energy
        #   ├── Renewable
        #   │     ├── Solar
        #   │     └── Wind
        #   └── Nuclear
        root = Node("Energy")
        renewable = Node("Renewable")
        root.add_child(renewable)
        renewable.add_child(Node("Solar", module={"id": 4}))
        renewable.add_child(Node("Wind", module={"id": 13}))
        root.add_child(Node("Nuclear", module={"id": 5}))
        return root

    def test_dfs_pre_order(self):
        root = self._sample_tree()
        order = [n.name for n in root.traverse_dfs()]
        self.assertEqual(order, ["Energy", "Renewable", "Solar", "Wind", "Nuclear"])

    def test_bfs_by_level(self):
        root = self._sample_tree()
        order = [n.name for n in root.traverse_bfs()]
        self.assertEqual(order, ["Energy", "Renewable", "Nuclear", "Solar", "Wind"])


class TestNodeOperations(unittest.TestCase):

    def _sample_tree(self):
        root = Node("Energy")
        renewable = Node("Renewable")
        root.add_child(renewable)
        renewable.add_child(Node("Solar", module={"id": 4, "generated": 80}))
        renewable.add_child(Node("Wind", module={"id": 13, "generated": 20}))
        root.add_child(Node("Nuclear", module={"id": 5, "generated": 80}))
        return root

    def test_find_by_name_hit(self):
        root = self._sample_tree()
        n = root.find("Solar")
        self.assertIsNotNone(n)
        self.assertEqual(n.module["id"], 4)

    def test_find_by_name_miss(self):
        root = self._sample_tree()
        self.assertIsNone(root.find("Unknown"))

    def test_leaves_returns_modules_only(self):
        root = self._sample_tree()
        ids = sorted(m["id"] for m in root.leaves())
        self.assertEqual(ids, [4, 5, 13])

    def test_depth(self):
        root = self._sample_tree()
        self.assertEqual(root.depth(), 3)  # Energy → Renewable → Solar

    def test_aggregate_sum_generation(self):
        root = self._sample_tree()
        total = root.aggregate(lambda m: m["generated"], initial=0, combine=lambda a, b: a + b)
        self.assertEqual(total, 180)

    def test_pretty_print_includes_all_names(self):
        root = self._sample_tree()
        out = root.pretty_print()
        for name in ["Energy", "Renewable", "Solar", "Wind", "Nuclear"]:
            self.assertIn(name, out)


if __name__ == "__main__":
    unittest.main()
