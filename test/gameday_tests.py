
from gameday import *
from unittest import TestSuite, TestCase, defaultTestLoader, TextTestRunner
from datetime import datetime


class GamedayTests(TestCase):

    def test_get_season_hitter_pitch_stats(self):
        game_date = datetime(year=2018, month=4, day=29)
        hitter_pitch_stats = get_previous_hitter_pitch_stats('400121', 'bal', game_date)
        # Test four-seam fastball stats
        self.assertEqual(int(hitter_pitch_stats['ff']['ab']), 25)
        self.assertEqual(int(hitter_pitch_stats['ff']['hr']), 1)
        self.assertEqual(int(hitter_pitch_stats['ff']['rbi']), 5)
        self.assertEqual(int(hitter_pitch_stats['ff']['bb']), 2)
        self.assertEqual(int(hitter_pitch_stats['ff']['so']), 3)
        self.assertEqual(float(hitter_pitch_stats['ff']['ops']), 0.913)
        # Test curveball stats
        self.assertEqual(int(hitter_pitch_stats['cu']['ab']), 5)
        self.assertEqual(int(hitter_pitch_stats['cu']['hr']), 0)
        self.assertEqual(int(hitter_pitch_stats['cu']['rbi']), 0)
        self.assertEqual(int(hitter_pitch_stats['cu']['bb']), 0)
        self.assertEqual(int(hitter_pitch_stats['cu']['so']), 0)
        self.assertAlmostEqual(float(hitter_pitch_stats['cu']['ops']), 0.600, delta=0.001)

    def test_get_season_pitcher_pitch_stats(self):
        game_date = datetime(year=2018, month=5, day=6)
        pitcher_pitch_stats = get_previous_pitcher_pitch_stats('519242', 'bos', game_date)

        # Test four-seam fastball stats
        self.assertEqual(int(pitcher_pitch_stats['ff']['ab']), 68)
        self.assertAlmostEqual(float(pitcher_pitch_stats['ff']['avg']), 0.235, delta=0.001)
        self.assertEqual(int(pitcher_pitch_stats['ff']['hr']), 3)
        self.assertEqual(int(pitcher_pitch_stats['ff']['rbi']), 6)
        self.assertEqual(int(pitcher_pitch_stats['ff']['bb']), 6)
        self.assertEqual(int(pitcher_pitch_stats['ff']['so']), 27)
        self.assertAlmostEqual(float(pitcher_pitch_stats['ff']['ops']), 0.731, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['ff']['rating']), 0.207, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['ff']['sweetness']), 1.207, delta=0.001)
        # Test slider stats
        self.assertEqual(int(pitcher_pitch_stats['sl']['ab']), 34)
        self.assertAlmostEqual(float(pitcher_pitch_stats['sl']['avg']), 0.118, delta=0.001)
        self.assertEqual(int(pitcher_pitch_stats['sl']['hr']), 1)
        self.assertEqual(int(pitcher_pitch_stats['sl']['rbi']), 2)
        self.assertEqual(int(pitcher_pitch_stats['sl']['bb']), 0)
        self.assertEqual(int(pitcher_pitch_stats['sl']['so']), 17)
        self.assertAlmostEqual(float(pitcher_pitch_stats['sl']['ops']), 0.402, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['sl']['rating']), -0.336, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['sl']['sweetness']), 0.664, delta=0.001)

    def test_get_pitcher_game_tendencies(self):
        game_date = datetime(year=2018, month=5, day=6)
        pitcher_pitch_stats = get_game_pitcher_tendencies('519242', 'bos', game_date)
        # Changeup stats
        self.assertEqual(int(pitcher_pitch_stats['CH']['num']), 22)
        self.assertAlmostEqual(float(pitcher_pitch_stats['CH']['pfx']), 11.04, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['CH']['vel']), 88.16, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['CH']['movement']), 8.93, delta=0.001)
        # Fastball stats
        self.assertEqual(int(pitcher_pitch_stats['FF']['num']), 27)
        self.assertAlmostEqual(float(pitcher_pitch_stats['FF']['pfx']), 10.41, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['FF']['vel']), 96.62, delta=0.001)
        self.assertAlmostEqual(float(pitcher_pitch_stats['FF']['movement']), 5.16, delta=0.001)
        print pitcher_pitch_stats


def suite():
    test_suite = TestSuite()
    test_suite.addTests(defaultTestLoader.loadTestsFromTestCase(GamedayTests))
    return test_suite

test_suite = suite()
test_runner = TextTestRunner()
test_runner.run(test_suite)
