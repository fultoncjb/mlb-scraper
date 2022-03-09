
from stat_miner import *
from unittest import TestCase


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






