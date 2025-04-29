import os

from stat_miner import *
import unittest
import sys
import stathead


class StatheadTests(unittest.TestCase):

    def get_creds(self):
        return os.environ.get("TEST_USERNAME"), os.environ.get("TEST_PWD")

    # def test_vs_pitcher(self):
    #     hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2003)
    #     vs_pitcher = stathead.get_vs_pitcher(hitter_id, 2007, 2009, self.get_creds())
    #     pass

    def test_new_vs_pitcher_abreu_pavano(self):
        hitter_stathead_id = "abreu-001bob"
        pitcher_stathead_id = "pavano001car"
        vs_gamelogs = stathead.get_vs_pitcher_gamelogs(hitter_stathead_id, "Abreu",
                                              pitcher_stathead_id, self.get_creds())
        self.assertEqual(int(sum(item["PA"] for item in vs_gamelogs)), 71)
        self.assertEqual(int(sum(item["AB"] for item in vs_gamelogs)), 59)
        self.assertEqual(int(sum(item["H"] for item in vs_gamelogs)), 20)
        self.assertEqual(int(sum(item["2B"] for item in vs_gamelogs)), 6)
        self.assertEqual(int(sum(item["3B"] for item in vs_gamelogs)), 0)
        self.assertEqual(int(sum(item["HR"] for item in vs_gamelogs)), 2)
        self.assertEqual(int(sum(item["RBI"] for item in vs_gamelogs)), 9)
        self.assertEqual(int(sum(item["BB"] for item in vs_gamelogs)), 10)
        self.assertEqual(int(sum(item["SO"] for item in vs_gamelogs)), 9)

    def test_new_vs_pitcher_abreu_beckett(self):
        hitter_stathead_id = "abreu-001bob"
        pitcher_stathead_id = "becket001jos"
        vs_pitcher = stathead.get_vs_pitcher_gamelogs(hitter_stathead_id, "Abreu",
                                             pitcher_stathead_id, self.get_creds())
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
        num_rbis = stathead.get_num_rbis("Reached on E5 (Ground Ball); Rollins Scores/unER; Abreu Scores/No RBI/unER; Howard to 3B; Dellucci to 2B",
                                "Dellucci")
        self.assertEqual(num_rbis, 0)

    def test_get_num_rbis_errors_no_rbi(self):
        num_rbis = stathead.get_num_rbis("Reached on E9 (Fly Ball to Deep RF); Gonzalez Scores/unER/No RBI; Green Scores/unER/No RBI; Sprague Scores/unER/No RBI; Delgado to 2B",
                                "Delgado")
        self.assertEqual(num_rbis, 0)

    def test_get_season_hitter_identifiers(self):
        """
        Get the season hitter identifiers and verify the count is correct and verify the content of the
        first and last element
        """
        hitter_ids = stathead.get_season_hitter_identifiers_and_pa(2022, self.get_creds())
        first_hitter_id = hitter_ids[0][0]
        self.assertEqual(len(hitter_ids), 200)
        self.assertEqual(first_hitter_id.get_id(), "judgeaa01")
        self.assertEqual(first_hitter_id.get_team(), "NYY")
        self.assertEqual(first_hitter_id.get_name(), "Aaron Judge")
        last_hitter_id = hitter_ids[-1][0]
        self.assertEqual(last_hitter_id.get_id(), "pasquvi01")
        self.assertEqual(last_hitter_id.get_team(), "KCR")
        self.assertEqual(last_hitter_id.get_name(), "Vinnie Pasquantino")

    def test_get_season_hitting_game_logs(self):
        gamelogs = stathead.get_season_hitting_game_logs("ortiz-001dav", 2004, self.get_creds())
        self.assertEqual(gamelogs.shape[0], 150)
        newest_date = gamelogs['Date'].max()
        newest_entry = gamelogs[gamelogs['Date'] == newest_date].iloc[0]
        keys = ['Rk', 'Player', 'Date', 'Age', 'Team', 'Opp', 'Result', 'PA', 'AB', 'R', 'H', '1B', '2B', '3B', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'TB', 'GIDP', 'HBP', 'SH', 'SF', 'IBB', 'BOP', 'Pos']
        dataframe_keys = gamelogs.columns
        for key in keys:
            self.assertTrue(key in dataframe_keys)
        self.assertEqual(newest_entry['Player'], 'David Ortiz')
        self.assertEqual(newest_entry['Date'], '2004-10-03')
        self.assertEqual(newest_entry['Age'], '28-320')
        self.assertEqual(newest_entry['Team'], 'BOS')
        self.assertEqual(newest_entry['Opp'], 'BAL')
        self.assertEqual(newest_entry['Result'], 'L, 2-3')
        self.assertEqual(newest_entry['PA'], 2)
        self.assertEqual(newest_entry['AB'], 1)
        self.assertEqual(newest_entry['R'], 0)
        self.assertEqual(newest_entry['H'], 0)
        self.assertEqual(newest_entry['1B'], 0)
        self.assertEqual(newest_entry['2B'], 0)
        self.assertEqual(newest_entry['3B'], 0)
        self.assertEqual(newest_entry['HR'], 0)
        self.assertEqual(newest_entry['RBI'], 0)
        self.assertEqual(newest_entry['SB'], 0)
        self.assertEqual(newest_entry['CS'], 0)
        self.assertEqual(newest_entry['BB'], 1)
        self.assertEqual(newest_entry['SO'], 0)
        self.assertEqual(newest_entry['BA'], 0)
        self.assertEqual(newest_entry['OBP'], 0.5)
        self.assertEqual(newest_entry['SLG'], 0)
        self.assertEqual(newest_entry['OPS'], 0.5)
        self.assertEqual(newest_entry['TB'], 0)
        self.assertEqual(newest_entry['GIDP'], 0)
        self.assertEqual(newest_entry['HBP'], 0)
        self.assertEqual(newest_entry['SH'], 0)
        self.assertEqual(newest_entry['SF'], 0)
        self.assertEqual(newest_entry['IBB'], 0)
        self.assertEqual(newest_entry['BOP'], 4)
        self.assertEqual(newest_entry['Pos'], 'DH')
        self.assertEqual(newest_entry['IsHome'], False)

    def test_get_career_hitting_stats(self):
        hitting_stats = stathead.get_career_hitting_stats("ramirma02", "Manny Ramirez", False, self.get_creds())
        self.assertEqual(hitting_stats["HR"], 555)
        self.assertEqual(hitting_stats["G"], 2302)
        self.assertEqual(hitting_stats["PA"], 9774)
        self.assertEqual(hitting_stats["AB"], 8244)
        self.assertEqual(hitting_stats["R"], 1544)
        self.assertEqual(hitting_stats["H"], 2574)
        self.assertEqual(hitting_stats["2B"], 547)
        self.assertEqual(hitting_stats["3B"], 20)
        self.assertEqual(hitting_stats["RBI"], 1831)
        self.assertEqual(hitting_stats["SB"], 38)
        self.assertEqual(hitting_stats["CS"], 33)
        self.assertEqual(hitting_stats["BB"], 1329)
        self.assertEqual(hitting_stats["SO"], 1813)
        self.assertEqual(hitting_stats["TB"], 4826)
        self.assertEqual(hitting_stats["GIDP"], 243)
        self.assertEqual(hitting_stats["HBP"], 109)
        self.assertEqual(hitting_stats["SH"], 2)
        self.assertEqual(hitting_stats["SF"], 90)
        self.assertEqual(hitting_stats["IBB"], 216)

    def test_weird_name_career_hitting_stats(self):
        hitting_stats = stathead.get_career_hitting_stats("o'neipa01", "Paul O'Neil", False, self.get_creds())
        self.assertEqual(hitting_stats["HR"], 281)

    def test_get_career_vs_ids(self):
        _, vs_ids = stathead.get_career_hitter_vs_ids("ramire002man", self.get_creds())
        self.assertEqual(vs_ids[0][0], "mussin001mic")
        self.assertEqual(vs_ids[0][1], 111)
        self.assertEqual(vs_ids[0][2], 24)
        self.assertEqual(vs_ids[-1][0], "tadano001kaz")
        self.assertEqual(vs_ids[-1][1], 1)
        self.assertEqual(vs_ids[-1][2], 0)
        self.assertEqual(len(vs_ids), 1224)


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'] + sys.argv[1:])