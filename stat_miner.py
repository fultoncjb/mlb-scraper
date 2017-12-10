"""
stat_miner.py
Top-level module used for mining stats for particular players and games
"""

from rotowire import *
from multiprocessing import Pool
from team_dict import *
from baseball_reference import *


class NoGamesFound(Exception):
    def __init__(self):
        super(NoGamesFound, self).__init__("No games found.")


def get_pregame_stats_wrapper(games, threading_enabled=True):

    if threading_enabled:
        thread_pool = Pool(6)
        thread_pool.map(get_pregame_stats, games)
    else:
        for game in games:
            get_pregame_stats(game)


def get_pregame_stats(game):
    game_miner = GameMiner(game)
    game_miner.mine_park_factors()
    game_miner.get_pregame_hitting_stats()
    game_miner.get_pregame_pitching_stats()


def mine_pregame_stats(threading_enabled=True):
    """ Mine the hitter/pitcher stats and predict the outcomes and commit to the database session
    """
    games = get_game_lineups()
    if len(games) == 0:
        raise NoGamesFound
    get_pregame_stats_wrapper(games, threading_enabled)


class HitterMiner(object):
    def __init__(self, baseball_reference_id):
        self._baseball_reference_id = baseball_reference_id
        self.career_stats = dict()
        self.vs_hand_stats = dict()
        self.vs_pitcher_stats = dict()
        self.recent_stats = dict()
        self.season_stats = dict()

    @staticmethod
    def get_id(full_name, team_abbreviation, year):
        return get_hitter_id(full_name, team_abbreviation, year)

    def mine_career_stats(self, hitter_career_soup=None):
        return get_career_hitting_stats(self._baseball_reference_id, hitter_career_soup)

    def mine_vs_hand_stats(self, pitcher_hand, hitter_career_soup=None):
        return get_vs_hand_hitting_stats(self._baseball_reference_id, pitcher_hand, hitter_career_soup)

    def mine_recent_stats(self, hitter_career_soup=None):
        return get_recent_hitting_stats(self._baseball_reference_id, hitter_career_soup)

    def mine_season_stats(self, year=None, soup=None):
        return get_season_hitting_stats(self._baseball_reference_id, year, soup)

    def mine_vs_pitcher_stats(self, pitcher_baseball_reference_id, vs_soup=None):
        return get_vs_pitcher_stats(self._baseball_reference_id, pitcher_baseball_reference_id, vs_soup)

    def mine_yesterdays_results(self):
        yesterdays_date = date.today() - timedelta(days=1)
        return get_hitting_game_log(self._baseball_reference_id, game_date=yesterdays_date)


class LineupMiner(object):
    def __init__(self, lineup, opposing_pitcher, game_date, game_time, is_home):
        self._lineup = lineup
        self._opposing_pitcher = opposing_pitcher
        self._game_date = game_date
        self._game_time = game_time
        self._is_home = is_home
        self._hitter_miners = list()

    def mine_pregame_stats(self):
        """ Fetch the pregame hitting stats from the web
        :return:
        """
        for current_hitter in self._lineup:
            baseball_reference_id = HitterMiner.get_id(current_hitter.name)
            hitter_miner = HitterMiner(baseball_reference_id)
            hitter_career_soup = get_hitter_page_career_soup(baseball_reference_id)
            hitter_miner.career_stats = current_hitter.mine_career_stats(hitter_career_soup)
            hitter_miner.vs_hand_stats = current_hitter.mine_vs_hand_stats(hitter_career_soup, self._opposing_pitcher.pitcher_hand)
            hitter_miner.recent_stats = current_hitter.mine_recent_stats(hitter_career_soup)
            hitter_miner.season_stats = current_hitter.mine_season_stats()
            hitter_miner.vs_pitcher_stats = current_hitter.mine_vs_pitcher_stats(self._opposing_pitcher.baseball_reference_id)
            self._hitter_miners.append(hitter_miner)


class PitcherMiner(object):
    def __init__(self, baseball_reference_id):
        self.baseball_reference_id = baseball_reference_id
        self.career_stats = dict()
        self.vs_stats = dict()
        self.recent_stats = dict()
        self.season_stats = dict()

    @staticmethod
    def get_id(full_name, team, year):
        return get_pitcher_id(full_name, team, year)

    def mine_pregame_stats(self):
        """ Get pregame stats for the given pitcher
        :param pitcher_id: unique Rotowire ID for the corresponing pitcher
        :param team: team abbreviation for the corresponding pitcher
        :param opposing_team: team abbreviation for the team the pitcher is facing
        :param database_session: SQLAlchemy database session
        :param game_date: the date of the game (in the following form yyyy-mm-dd)
        :return: a PregamePitcherGameEntry object without the predicted_draftkings_points field populated
        """
        pitcher_career_soup = get_pitcher_page_career_soup(self.baseball_reference_id)
        self.career_stats = self.mine_career_stats(pitcher_career_soup)
        self.recent_stats = self.mine_recent_stats(pitcher_career_soup)
        self.season_stats = self.mine_season_stats()

    def mine_career_stats(self, pitcher_career_soup=None):
        return get_career_pitching_stats(self.baseball_reference_id, pitcher_career_soup)

    def mine_recent_stats(self, pitcher_career_soup=None):
        return get_recent_pitcher_stats(self.baseball_reference_id, pitcher_career_soup)

    def mine_season_stats(self, year=None, soup=None):
        return get_season_pitcher_stats(self.baseball_reference_id, year, soup)

    def mine_yesterdays_results(self):
        yesterdays_date = date.today() - timedelta(days=1)
        return get_pitching_game_log(self.baseball_reference_id, game_date=yesterdays_date)


class GameMiner(object):
    def __init__(self, game):

        self._game = game
        self._home_lineup_miner = LineupMiner(game.home_lineup, game.away_pitcher, game.game_date,
                                              game.game_time, is_home=True)
        # TODO should have the ability to specify the baseball reference ID so we can use the database
        baseball_reference_id = PitcherMiner.get_id(game.home_pitcher.name, game.home_pitcher.team, game.game_date.year)
        self._home_pitcher_miner = PitcherMiner(baseball_reference_id)
        self._away_lineup_miner = LineupMiner(game.away_lineup, game.home_pitcher, game.game_date,
                                              game.game_time, is_home=False)
        baseball_reference_id = PitcherMiner.get_id(game.away_pitcher.name, game.away_pitcher.team, game.game_date.year)
        self._away_pitcher_miner = PitcherMiner(baseball_reference_id)

    def get_pregame_hitting_stats(self):
        self._away_lineup_miner.mine_pregame_stats()
        self._home_lineup_miner.mine_pregame_stats()

    def get_pregame_pitching_stats(self):
        self._home_pitcher_miner.mine_pregame_stats()
        self._away_pitcher_miner.mine_pregame_stats()

    def mine_park_factors(self):
        team_abbrev = self._home_pitcher_miner.get_team()
        return get_team_info(get_baseball_reference_team(team_abbrev), self._game.game_date.year)


class UmpireMiner(object):

    def mine_umpire_data(self):
        url = "https://swishanalytics.com/mlb/mlb-umpire-factors"
        umpire_soup = get_soup_from_url(url)

        stat_table = umpire_soup.find("table", {"id": "ump-table"}).find("tbody")

        ump_dict = dict()
        if stat_table is not None:
            ump_rows = stat_table.findAll("tr")
            for ump_row in ump_rows:
                ump_data = ump_row.findAll("td")
                ump_entry = dict()

                ump_entry["K %"] = float(ump_data[3].text.strip().replace("%", "")) / 100
                ump_entry["BB %"] = float(ump_data[4].text.strip().replace("%", "")) / 100
                ump_entry["RPG"] = float(ump_data[5].text.strip())
                ump_entry["BA"] = float(ump_data[6].text.strip())
                ump_entry["OBP"] = float(ump_data[7].text.strip())
                ump_entry["SLG"] = float(ump_data[8].text.strip())

                ump_entry["K Boost"] = float(ump_data[9].text.strip().replace("x", ""))
                ump_entry["BB Boost"] = float(ump_data[10].text.strip().replace("x", ""))
                ump_entry["R Boost"] = float(ump_data[11].text.strip().replace("x", ""))
                ump_entry["BA Boost"] = float(ump_data[12].text.strip().replace("x", ""))
                ump_entry["OBP Boost"] = float(ump_data[13].text.strip().replace("x", ""))
                ump_entry["SLG Boost"] = float(ump_data[14].text.strip().replace("x", ""))

                ump_dict[ump_data[0].text.strip()] = ump_entry

        return ump_dict