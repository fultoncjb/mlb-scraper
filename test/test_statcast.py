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

    def test_exit_velocity(self):
        ev_data = statcast.get_exit_velocity(2024)
        self.assertEqual(ev_data.shape, (647, 18))
        self.assertEqual(ev_data["Player"][0], "Stone Garrett")
        self.assertEqual(ev_data["BBE"][0], 5)
        self.assertEqual(ev_data["LA (°)"][0], 20.5)
        self.assertEqual(ev_data["LA SwSp%"][0], 60.0)
        self.assertEqual(ev_data["Exit Velocity (MPH) Max"][0], 107.8)
        self.assertEqual(ev_data["Exit Velocity (MPH) Avg"][0], 100)
        self.assertEqual(ev_data["Exit Velocity (MPH) EV50"][0], 103.6)
        self.assertEqual(ev_data["Exit Velocity (MPH) FB/LD"][0], 101.7)
        self.assertEqual(ev_data["Distance (ft) Max"][0], 431)
        self.assertEqual(ev_data["Distance (ft) Avg HR"][0], 431)
        self.assertEqual(ev_data["Hard Hit 95 MPH+"][0], 4)
        self.assertEqual(ev_data["Hard Hit %"][0], 80.0)
        self.assertEqual(ev_data["Hard Hit % Swing"][0], 25.0)
        self.assertEqual(ev_data["Barrels #"][0], 2)
        self.assertEqual(ev_data["Barrels Brls/BBE %"][0], 40.0)
        self.assertEqual(ev_data["Barrels Brls/PA %"][0], 33.3)
        self.assertEqual(ev_data["Id"][0], "656448")