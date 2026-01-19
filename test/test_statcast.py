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
        self.assertEqual(factors["Rockies"].factor, 115)

        # Check the Red Sox park factors
        self.assertEqual(factors["Red Sox"].id, 3)
        self.assertEqual(factors["Red Sox"].venue_name, "Fenway Park")
        self.assertEqual(factors["Red Sox"].factor, 103)

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

    def test_baserunning_run_value(self):
        stats = statcast.get_baserunning_run_value(2024)
        self.assertEqual(stats.shape, (189, 16))
        self.assertEqual(stats["Player"][0], "Corbin Carroll")
        self.assertEqual(stats["Baserunning Runs"][0], 12)
        self.assertEqual(stats["Runs via Extra Bases Taken"][0], 9)
        self.assertEqual(stats["Runs via Stolen Bases"][0], 4)
        self.assertEqual(stats["Total Advance Attempts"][0], 120)
        self.assertEqual(stats["Advances"][0], 10)
        self.assertEqual(stats["Thrown Out"][0], 0)
        self.assertEqual(stats["Holds"][0], -1)
        self.assertEqual(stats["XB Advance Attempts"][0], 78)
        self.assertEqual(stats["SB (2B) Runs"][0], 3)
        self.assertEqual(stats["SB (3B) Runs"][0], 1)
        self.assertEqual(stats["SB (2B) Advances vs Avg"][0], 18)
        self.assertEqual(stats["SB (3B) Advances vs Avg"][0], 4)
        self.assertEqual(stats["SB Advance Attempts"][0], 42)
        self.assertEqual(stats["Id"][0], "682998")

    def test_hitting_run_value(self):
        stats = statcast.get_hitter_run_value(2024)
        self.assertEqual(stats.shape, (300, 11))
        self.assertEqual(stats["Player"][0], "Aaron Judge")
        self.assertEqual(stats["PA"][0], 683)
        # TODO need to fix the presence of the comma
        # self.assertEqual(stats["Pitches"][0], 2882)
        self.assertEqual(stats["Runs Heart"][0], 40)
        self.assertEqual(stats["Runs Shadow"][0], 9)
        self.assertEqual(stats["Runs Chase"][0], 31)
        self.assertEqual(stats["Runs Waste"][0], 17)
        self.assertEqual(stats["Runs All"][0], 97)
        self.assertEqual(stats["Id"][0], "592450")

    def test_pitching_run_value(self):
        # TODO
        pass

    def test_hitting_pitch_arsenal(self):
        # TODO
        pass

    def test_pitching_pitch_arsenal(self):
        # TODO
        pass