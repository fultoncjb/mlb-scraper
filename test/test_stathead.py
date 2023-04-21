
from stat_miner import *
import unittest
import sys
from stathead import *


class StatheadTests(unittest.TestCase):

    def test_vs_pitcher(self):
        hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2003)
        vs_pitcher = get_vs_pitcher(hitter_id, 2007, 2009, (StatheadTests.USERNAME, StatheadTests.PASSWORD))

    def test_new_vs_pitcher_abreu_pavano(self):
        hitter_id = HitterMiner.get_id("Bobby Abreu", "PHI", 1998)
        vs_pitcher = get_vs_pitcher_gamelogs(hitter_id, "pavanca01", (StatheadTests.USERNAME, StatheadTests.PASSWORD))
        self.assertEqual(int(sum(item["PA"] for item in vs_pitcher)), 71)
        self.assertEqual(int(sum(item["AB"] for item in vs_pitcher)), 59)
        self.assertEqual(int(sum(item["H"] for item in vs_pitcher)), 20)
        self.assertEqual(int(sum(item["2B"] for item in vs_pitcher)), 6)
        self.assertEqual(int(sum(item["3B"] for item in vs_pitcher)), 0)
        self.assertEqual(int(sum(item["HR"] for item in vs_pitcher)), 2)
        self.assertEqual(int(sum(item["RBI"] for item in vs_pitcher)), 9)
        self.assertEqual(int(sum(item["BB"] for item in vs_pitcher)), 10)
        self.assertEqual(int(sum(item["SO"] for item in vs_pitcher)), 9)

    def test_new_vs_pitcher_abreu_beckett(self):
        hitter_id = HitterMiner.get_id("Bobby Abreu", "PHI", 1998)
        vs_pitcher = get_vs_pitcher_gamelogs(hitter_id, "beckejo02", (StatheadTests.USERNAME, StatheadTests.PASSWORD))
        self.assertEqual(int(sum(item["PA"] for item in vs_pitcher)), 103)
        self.assertEqual(int(sum(item["AB"] for item in vs_pitcher)), 82)
        self.assertEqual(int(sum(item["H"] for item in vs_pitcher)), 15)
        self.assertEqual(int(sum(item["2B"] for item in vs_pitcher)), 3)
        self.assertEqual(int(sum(item["3B"] for item in vs_pitcher)), 0)
        self.assertEqual(int(sum(item["HR"] for item in vs_pitcher)), 2)
        self.assertEqual(int(sum(item["RBI"] for item in vs_pitcher)), 7)
        self.assertEqual(int(sum(item["BB"] for item in vs_pitcher)), 21)
        self.assertEqual(int(sum(item["SO"] for item in vs_pitcher)), 25)

    def test_get_num_rbis_errors(self):
        hitter_id = PlayerIdentifier("David Dellucci", "delluda01")
        num_rbis = get_num_rbis("Reached on E5 (Ground Ball); Rollins Scores/unER; Abreu Scores/No RBI/unER; Howard to 3B; Dellucci to 2B",
                                hitter_id)
        self.assertEqual(num_rbis, 1)

    def test_get_num_rbis_errors_no_rbi(self):
        hitter_id = PlayerIdentifier("Carlos Delgado", "delgaca01")
        num_rbis = get_num_rbis("Reached on E9 (Fly Ball to Deep RF); Gonzalez Scores/unER/No RBI; Green Scores/unER/No RBI; Sprague Scores/unER/No RBI; Delgado to 2B",
                                hitter_id)
        self.assertEqual(num_rbis, 0)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        StatheadTests.USERNAME = sys.argv.pop()
        StatheadTests.PASSWORD = sys.argv.pop()
    unittest.main()