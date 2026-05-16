"""Tests for the two trees built over the flat MODULES list."""

import unittest

from colony.hierarchies import build_functional_tree, build_criticality_tree


class TestFunctionalTree(unittest.TestCase):

    def setUp(self):
        self.root = build_functional_tree()

    def test_root_name(self):
        self.assertEqual(self.root.name, "Aurora Siger Colony")

    def test_four_branches(self):
        branches = [c.name for c in self.root.children]
        self.assertEqual(set(branches), {"Energy", "Life Support", "Command", "Operations"})

    def test_energy_holds_three_generators(self):
        energy = self.root.find("Energy")
        names = {c.name for c in energy.children}
        self.assertEqual(names, {"Solar Power", "Nuclear Power", "Wind Power"})

    def test_total_leaves(self):
        self.assertEqual(len(self.root.leaves()), 13)


class TestCriticalityTree(unittest.TestCase):

    def setUp(self):
        self.root = build_criticality_tree()

    def test_three_levels(self):
        branches = [c.name for c in self.root.children]
        self.assertEqual(branches, ["Vital", "Sustenance", "Expansion"])

    def test_vital_contains_eclss_and_habitat(self):
        vital = self.root.find("Vital")
        names = {c.name for c in vital.children}
        self.assertIn("Life Support (ECLSS)", names)
        self.assertIn("Habitat", names)

    def test_expansion_contains_workshop_and_lab(self):
        expansion = self.root.find("Expansion")
        names = {c.name for c in expansion.children}
        self.assertIn("Workshop and Maintenance", names)
        self.assertIn("Science Lab", names)

    def test_total_leaves(self):
        self.assertEqual(len(self.root.leaves()), 13)


class TestSharedReferences(unittest.TestCase):
    """The two trees must reference the SAME module dicts."""

    def test_same_reference_for_eclss(self):
        functional = build_functional_tree()
        criticality = build_criticality_tree()
        eclss_f = functional.find("Life Support (ECLSS)").module
        eclss_c = criticality.find("Life Support (ECLSS)").module
        self.assertIs(eclss_f, eclss_c)


if __name__ == "__main__":
    unittest.main()
