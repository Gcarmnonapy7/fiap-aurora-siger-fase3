"""Tests for the flat module list of the colony."""

import unittest

from colony.modules import MODULES, find_module


class TestModules(unittest.TestCase):

    def test_total_modules(self):
        """Must have 13 modules: 12 from Fase 2 + Wind Power."""
        self.assertEqual(len(MODULES), 13)

    def test_sequential_ids(self):
        ids = [m["id"] for m in MODULES]
        self.assertEqual(ids, list(range(1, 14)))

    def test_wind_power_is_id_13(self):
        wind = find_module(13)
        self.assertEqual(wind["name"], "Wind Power")
        self.assertEqual(wind["type"], "wind_generator")

    def test_generators_have_capacity(self):
        for id_ in [4, 5, 13]:
            self.assertIn("max_capacity_kw", find_module(id_))

    def test_pressurized_modules_have_positive_thermal_factor(self):
        """Habitat, ECLSS, Medical, Lab, Workshop."""
        pressurized = {3, 2, 7, 12, 11}
        for m in MODULES:
            if m["id"] in pressurized:
                self.assertGreater(m["thermal_factor"], 0)

    def test_modules_that_scale_with_surplus(self):
        """Food (8), ISRU (10), Lab (12)."""
        expected = {8, 10, 12}
        found = {m["id"] for m in MODULES if m["scales_with_surplus"]}
        self.assertEqual(found, expected)

    def test_minimum_lower_or_equal_to_adequate(self):
        for m in MODULES:
            c = m["consumption_by_mode"]
            self.assertLessEqual(c["minimum"], c["adequate"])

    def test_find_module_raises_when_missing(self):
        with self.assertRaises(KeyError):
            find_module(999)


if __name__ == "__main__":
    unittest.main()
