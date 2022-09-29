
import fan_graphs
from unittest import TestCase


class FanGraphsTests(TestCase):

    def test_vs_pitcher(self):
        hitter_id = fan_graphs.get_hitter_id("David Ortiz", "red-sox", 2004)
        print(hitter_id)