
from stat_miner import *
from baseball_reference import *
from unittest import TestCase
import functools


class BaseballReferenceTests(TestCase):

    def test_get_season_hitter_stats(self):
        hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2010)
        hitter_miner = HitterMiner(hitter_id)
        season_stats = hitter_miner.mine_season_stats(2013)

        self.assertEqual(int(season_stats['G']), 137)
        self.assertEqual(int(season_stats['GS']), 135)
        self.assertEqual(int(season_stats['PA']), 600)
        self.assertEqual(int(season_stats['AB']), 518)
        self.assertEqual(int(season_stats['R']), 84)
        self.assertEqual(int(season_stats['H']), 160)
        self.assertEqual(int(season_stats['2B']), 38)
        self.assertEqual(int(season_stats['3B']), 2)
        self.assertEqual(int(season_stats['HR']), 30)
        self.assertEqual(int(season_stats['RBI']), 103)
        self.assertEqual(int(season_stats['SB']), 4)
        self.assertEqual(int(season_stats['CS']), 0)
        self.assertEqual(int(season_stats['BB']), 76)
        self.assertEqual(int(season_stats['SO']), 88)
        self.assertAlmostEqual(float(season_stats['BA']), 0.309, 3)
        self.assertAlmostEqual(float(season_stats['OBP']), 0.395, 3)
        self.assertAlmostEqual(float(season_stats['SLG']), 0.564, 3)
        self.assertAlmostEqual(float(season_stats['OPS']), 0.959, 3)
        self.assertEqual(int(season_stats['TB']), 292)
        self.assertEqual(int(season_stats['GDP']), 21)
        self.assertEqual(int(season_stats['HBP']), 1)
        self.assertEqual(int(season_stats['SH']), 0)
        self.assertEqual(int(season_stats['SF']), 5)
        self.assertEqual(int(season_stats['IBB']), 27)
        self.assertEqual(int(season_stats['ROE']), 6)
        self.assertAlmostEqual(float(season_stats['BAbip']), 0.321, 3)
        self.assertEqual(int(season_stats['tOPS+']), 100)
        self.assertEqual(int(season_stats['sOPS+']), 167)

    def test_get_season_pitcher_stats(self):
        pitcher_id = PitcherMiner.get_id("Pedro Martinez", "BOS", 2001)
        pitcher_miner = PitcherMiner(pitcher_id)
        season_stats = pitcher_miner.mine_season_stats(1999)

        self.assertEqual(int(season_stats['W']), 23)
        self.assertEqual(int(season_stats['L']), 4)
        self.assertAlmostEqual(float(season_stats['ERA']), 2.07)
        self.assertEqual(int(season_stats['G']), 31)
        self.assertEqual(int(season_stats['GS']), 29)
        self.assertEqual(int(season_stats['GF']), 1)
        self.assertEqual(int(season_stats['CG']), 5)
        self.assertEqual(int(season_stats['SHO']), 1)
        self.assertEqual(int(season_stats['SV']), 0)
        self.assertAlmostEqual(float(season_stats['IP']), 213.1)
        self.assertEqual(int(season_stats['H']), 160)
        self.assertEqual(int(season_stats['R']), 56)
        self.assertEqual(int(season_stats['ER']), 49)
        self.assertEqual(int(season_stats['HR']), 9)
        self.assertEqual(int(season_stats['BB']), 37)
        self.assertEqual(int(season_stats['IBB']), 1)
        self.assertEqual(int(season_stats['SO']), 313)
        self.assertEqual(int(season_stats['HBP']), 9)
        self.assertEqual(int(season_stats['BK']), 0)
        self.assertEqual(int(season_stats['WP']), 6)
        self.assertEqual(int(season_stats['BF']), 835)
        self.assertAlmostEqual(float(season_stats['WHIP']), 0.923)
        self.assertAlmostEqual(float(season_stats['SO9']), 13.2)
        self.assertAlmostEqual(float(season_stats['SO/W']), 8.46)

    def test_get_career_hitting_stats(self):
        hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2003)
        hitter_miner = HitterMiner(hitter_id)
        career_stats = hitter_miner.mine_career_stats()
        self.assertEqual(int(career_stats['G']), 2408 + 85)
        self.assertEqual(int(career_stats['PA']), 10091 + 369)
        self.assertEqual(int(career_stats['AB']), 8640 + 304)
        self.assertEqual(int(career_stats['R']), 1419 + 51)
        self.assertEqual(int(career_stats['H']), 2472 + 88)
        self.assertEqual(int(career_stats['2B']), 632 + 22)
        self.assertEqual(int(career_stats['3B']), 19 + 2)
        self.assertEqual(int(career_stats['HR']), 541 + 17)
        self.assertEqual(int(career_stats['RBI']), 1768 + 61)
        self.assertEqual(int(career_stats['SB']), 17 + 0)
        self.assertEqual(int(career_stats['CS']), 9 + 1)
        self.assertEqual(int(career_stats['BB']), 1319 + 59)
        self.assertEqual(int(career_stats['SO']), 1750 + 72)
        self.assertEqual(int(career_stats['TB']), 4765 + 165)
        self.assertEqual(int(career_stats['GDP']), 236 + 4)
        self.assertEqual(int(career_stats['HBP']), 38 + 2)
        self.assertEqual(int(career_stats['SH']), 2 + 0)
        self.assertEqual(int(career_stats['SF']), 92 + 4)
        self.assertEqual(int(career_stats['IBB']), 209 + 11)

    def test_season_hitting_game_log(self):
        hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2003)
        season_hitting_stats = get_season_hitting_game_logs(hitter_id, 2003)
        self.assertTrue(len(season_hitting_stats) > 0)






