
from gameday import *
from unittest import TestSuite, TestCase, defaultTestLoader, TextTestRunner
from datetime import datetime


class GamedayTests(TestCase):

    def test_get_season_hitter_pitch_stats(self):
        game_date = datetime.today()
        hitter_pitch_stats = get_season_hitter_pitch_stats('400121', 'bal', game_date)
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

def suite():
    test_suite = TestSuite()
    test_suite.addTests(defaultTestLoader.loadTestsFromTestCase(GamedayTests))
    return test_suite

test_suite = suite()
test_runner = TextTestRunner()
test_runner.run(test_suite)
