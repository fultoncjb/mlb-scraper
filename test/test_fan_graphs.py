
import fan_graphs
from unittest import TestCase


class FanGraphsTests(TestCase):

    def test_get_id(self):
        hitter_id_tuple = fan_graphs.get_hitter_id("David Ortiz", "red-sox", 2004)
        self.assertEqual(hitter_id_tuple[0], "david-ortiz/745")
        self.assertEqual(hitter_id_tuple[1], "DH")

    def test_vs_fastball(self):
        hitter_id_tuple = fan_graphs.get_hitter_id("David Ortiz", "red-sox", 2004)
        stats = fan_graphs.get_hitter_stats_vs_pitch(hitter_id_tuple, 2007, "FA")
        self.assertEqual(int(stats["Pitches"]), 283)
        self.assertEqual(int(stats["AB"]), 56)
        self.assertEqual(int(stats["PA"]), 66)
        self.assertEqual(int(stats["H"]), 23)
        self.assertEqual(int(stats["1B"]), 9)
        self.assertEqual(int(stats["2B"]), 6)
        self.assertEqual(int(stats["3B"]), 0)
        self.assertEqual(int(stats["HR"]), 8)
        self.assertEqual(int(stats["BB"]), 10)
        self.assertEqual(int(stats["IBB"]), 0)
        self.assertEqual(int(stats["SO"]), 6)
        self.assertEqual(int(stats["HBP"]), 0)
        self.assertEqual(int(stats["SF"]), 0)
        self.assertEqual(int(stats["SH"]), 0)
        self.assertEqual(int(stats["GDP"]), 2)
        self.assertAlmostEqual(float(stats["AVG"]), 0.411)
        self.assertAlmostEqual(float(stats["minVel"]), 63.5)
        self.assertAlmostEqual(float(stats["maxVel"]), 99.3)
        self.assertAlmostEqual(float(stats["Vel"]), 91.1)
