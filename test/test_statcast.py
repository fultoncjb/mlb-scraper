import os

import unittest
import sys
import statcast


class StatheadTests(unittest.TestCase):

    def test_ballpark_factors(self):
        factors = statcast.get_park_factors(2025)

        # Check the Rockies park factors
        self.assertEqual(factors["Rockies"].id, 19)
        self.assertEqual(factors["Rockies"].venue_name, "Coors Field")
        self.assertEqual(factors["Rockies"].factor, 112)

        # Check the Red Sox park factors
        self.assertEqual(factors["Red Sox"].id, 3)
        self.assertEqual(factors["Red Sox"].venue_name, "Fenway Park")
        self.assertEqual(factors["Red Sox"].factor, 105)