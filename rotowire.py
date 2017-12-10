"""
rotowire.py
Module used for scraping data from rotowire.com
"""

from datetime import datetime, date
from team_dict import *
from baseball_reference import get_team_info, TableNotFound
from beautiful_soup_helper import get_soup_from_url

# Daily lineups relevant HTML labels
DAILY_LINEUPS_URL = "http://www.rotowire.com/baseball/daily_lineups.htm"
GAME_REGION_LABEL = "offset1 span15"
TEAM_REGION_LABEL = "span15 dlineups-topbox"
AWAY_TEAM_REGION_LABEL = "span5 dlineups-topboxleft"
HOME_TEAM_REGION_LABEL = "span5 dlineups-topboxright"
GAME_INFO_LABEL = "dlineups-topboxcenter"
TIME_REGION_LABEL = "dlineups-topboxcenter-topline"
AWAY_TEAM_PLAYER_LABEL = "dlineups-vplayer"
HOME_TEAM_PLAYER_LABEL = "dlineups-hplayer"
LINEUPS_CLASS_LABEL = "span15 dlineups-mainbox"
POSITION_CLASS_LABEL = "dlineups-pos"
PITCHERS_REGION_LABEL = "span11 dlineups-pitchers"
HAND_CLASS_LABEL = "dlineups-lr"
DRAFTKINGS_LINK_LABEL = "span15 dlineups-promo-bottom"

# Individual player page relevant HTML labels
PLAYER_PAGE_BASE_URL = "http://www.rotowire.com/baseball/player.htm?id="
PLAYER_PAGE_LABEL = "span16 mlb-player-nameteam"
PLAYER_PAGE_CAREER_BASE_URL = "http://www.rotowire.com/baseball/plcareer.htm?id="
YEAR_TABLE_LABEL = "basicstats"
TABLE_ENTRY_LABEL = "mlbstat-year"
RECENT_TABLE_LABEL = "gamelog"
BATTER_SPLIT_BASE_URL = "http://www.rotowire.com/baseball/battersplit.htm?id="

# Split stats relevent HTML labels
SPLIT_TABLE_LABEL = "tablesorter makesortable"

WIND_LABEL = "dlineups-topboxcenter-bottomline"


class PlayerStruct(object):
    def __init__(self, team, rotowire_id, position, hand):
        self.team = team
        self.rotowire_id = rotowire_id
        self.position = position
        self.hand = hand
        self.name = ''

    def __eq__(self, other):
        return self.team == other.team and self.rotowire_id == other.rotowire_id and \
               self.position == other.position and self.hand == other.hand


class Game(object):
    def __init__(self, away_lineup, away_pitcher, home_lineup, home_pitcher, game_date, game_time):
        self.home_lineup = home_lineup
        self.away_lineup = away_lineup
        self.away_pitcher = away_pitcher
        self.home_pitcher = home_pitcher
        self.game_date = game_date
        self.game_time = game_time
        self.umpire_name = None
        self.wind_speed = 0
        self.temperature = 70

    def is_valid(self):
        if len(self.away_lineup) != 9 or len(self.home_lineup) != 9:
            return False

        return True


class GameMatchup(object):
    def __init__(self):
        self.away_pitcher = None
        self.home_pitcher = None
        self.home_team = None
        self.away_team = None
        self.game_date = None
        self.game_time = None


class GameFactors(object):
    def __init__(self, wind_speed, ump_name, pitcher_park_score, hitter_park_score):
        self.wind_speed = wind_speed
        self.ump_name = ump_name
        self.pitcher_park_score = pitcher_park_score
        self.hitter_park_score = hitter_park_score


class HomeAwayEnum(object):
    AWAY = 0
    HOME = 1


def get_game_lineups(url=None, game_date=None):
    """ Mine the RotoWire daily lineups page and get the players' name, team, and RotoWire ID
    Commit the GameEntry objects to the database.
    :param game_date: datetime date object of the game date (default is None)
    :param url: the URL containing the daily lineups (default is None)
    :return: list of Game objects representing the lineups for the day
    """

    if url is None:
        url = DAILY_LINEUPS_URL

    if game_date is None:
        game_date = date.today()

    """TODO: add feature to look if it's going to rain"""
    lineup_soup = get_soup_from_url(url)
    header_nodes = lineup_soup.findAll("div", {"class": TEAM_REGION_LABEL})
    games = list()
    for header_node in header_nodes:
        game_node = header_node.parent
        home_team_lineup = list()
        away_team_lineup = list()
        try:
            away_team_abbreviation = game_node.find("div", {"class": AWAY_TEAM_REGION_LABEL}).text.split()[0]
            home_team_abbreviation = game_node.find("div", {"class": HOME_TEAM_REGION_LABEL}).text.split()[0]
            game_main_soup = game_node.find("div", {"class": LINEUPS_CLASS_LABEL})
            game_time = game_node.find("div", {"class": TIME_REGION_LABEL}).find("a").text.replace("ET", "").strip()
            game_time = datetime.strptime(game_time, '%I:%M %p').strftime("%H:%M")

            for away_player in game_main_soup.findAll("div", {"class": AWAY_TEAM_PLAYER_LABEL}):
                away_team_lineup.append(get_hitter(away_player, away_team_abbreviation))
            for home_player in game_main_soup.findAll("div", {"class": HOME_TEAM_PLAYER_LABEL}):
                home_team_lineup.append(get_hitter(home_player, home_team_abbreviation))

            pitchers = game_node.find("div", PITCHERS_REGION_LABEL).findAll("div")
            away_team_pitcher = get_pitcher(pitchers[0], away_team_abbreviation)
            home_team_pitcher = get_pitcher(pitchers[1], home_team_abbreviation)
        # No pitchers present on page
        except AttributeError:
            print "Game between %s and %s is not valid." % (away_team_abbreviation, home_team_abbreviation)
            continue

        current_game = Game(away_team_lineup, away_team_pitcher, home_team_lineup, home_team_pitcher, str(game_date), str(game_time))

        if current_game.is_valid():
            game_factors = get_external_game_factors(game_node)
            current_game.wind_speed = game_factors.wind_speed
            current_game.umpire_name = game_factors.ump_name
            games.append(current_game)
        else:
            print "Game between %s and %s is not valid." % (away_team_abbreviation, home_team_abbreviation)

    return games


def get_external_game_factors(game_node):
    """
    :param game_node: BeautifulSoup object containing the game from the daily lineups page
    :return: a GameEntry containing the
    """
    try:
        home_team_abbreviation = game_node.find("div", {"class": HOME_TEAM_REGION_LABEL}).text.split()[0]
        wind_speed = get_wind_speed(game_node)
        """TODO: add temperature
        For now, we will use nominal temperature and umpire readings
        """
        ump_name = None
        try:
            ump_name = get_ump_name(game_node)
        except UmpDataNotFound:
            print "Ump data not found."
        park_hitter_score, park_pitcher_score = get_team_info(get_baseball_reference_team(home_team_abbreviation))
        game_factors = GameFactors(wind_speed, ump_name, park_pitcher_score, park_hitter_score)
    except AttributeError:
        game_factors = None

    return game_factors


def get_id(soup):
    """ Get the RotoWire ID from a BeautifulSoup node
    :param soup: BeautifulSoup object of the player in the daily lineups page
    """
    return soup.find("a").get("href").split("id=")[1]


def get_hitter(soup, team):
    """ Get a PlayerStruct representing a hitter
    If a database session is not provided, open the player page to obtain the hitter info.
    Otherwise, look for the hitter in the database. If not found, open the player page to obtain the hitter info.
    :param soup: BeautifulSoup object of the hitter in the daily lineups page
    :param team: team abbreviation of the hitter
    :param database_session: SQLAlchemy database session (default is None)
    """
    rotowire_id = get_id(soup)
    position = soup.find("div", {"class": POSITION_CLASS_LABEL}).text
    hand = get_hand(soup)

    return PlayerStruct(team, rotowire_id, position, hand)


def get_pitcher(soup, team):
    """ Get a PlayerStruct representing a pitcher
    If a database session is not provided, open the player page to obtain the pitcher info.
    Otherwise, look for the pitcher in the database. If not found, open the player page to obtain the pitcher info.
    :param soup: BeautifulSoup object of the pitcher in the daily lineups page
    :param team: team abbreviation of the pitcher
    :param database_session: SQLAlchemy database session (default is None)
    """
    rotowire_id = get_id(soup)
    hand = get_hand(soup)

    return PlayerStruct(team, rotowire_id, "P", hand)


def get_hand(soup):
    """
    :param soup: BeautifulSoup node of the player
    :return: Hand of the player
    """
    return soup.find("span", {"class": HAND_CLASS_LABEL}).text.strip().replace("(", "").replace(")", "")


def get_name_from_id(rotowire_id):
    """ Use the acquired RotoWire ID to resolve the name in case it is too long for the
    daily lineups page.
    :param rotowire_id: unique ID for a player in RotoWire
    :return: str representation of the name of the player
    """
    player_soup = get_soup_from_url(PLAYER_PAGE_BASE_URL + str(rotowire_id))
    return player_soup.find("div", {"class": PLAYER_PAGE_LABEL}).find("h1").text.strip()

class HitterNotFound(Exception):
    def __init__(self, id_str):
        super(HitterNotFound, self).__init__("Hitter '%s' not found in the database" % id_str)


class PitcherNotFound(Exception):
    def __init__(self, id_str):
        super(PitcherNotFound, self).__init__("Pitcher '%s' not found in the database" % id_str)

def table_entry_to_int(entry):
    return int(entry.replace(",", ""))


def get_table_row_dict(soup, table_name, table_row_label, table_column_label):
    """ Get a dictionary representation of the given row in the table
    :param soup: BeautifulSoup object containing a single "table" HTML object
    :param table_name: HTML "id" field for the table
    :param table_row_label: HTML label for the row of the table
    :param table_column_label: HTML label for the column
    :return: dictionary representation of the given row
    """
    try:
        results_table = soup.find("table", {"id": table_name})
        if results_table is None:
            raise TableNotFound(table_name)

        table_header_list = results_table.find("thead").findAll("th")
        table_header_list = [x.text for x in table_header_list]
        stat_rows = results_table.find("tbody").findAll("tr")
    except AttributeError:
        raise TableNotFound(table_name)

    for stat_row in stat_rows:
        #Create a dictionary of the stat attributes
        stat_dict = dict()
        stat_entries = stat_row.findAll("td")
        for i in range(0, len(table_header_list)):
            if stat_entries[i].text == "":
                stat_dict[table_header_list[i]] = 0
            else:
                stat_dict[table_header_list[i]] = stat_entries[i].text
        try:
            if stat_dict[table_column_label] == table_row_label:
                return stat_dict
        # We have reached the end of the year-by-year stats, just end
        except ValueError:
            break

    # TODO: add a TableRowNotFound exception
    raise TableNotFound(table_name)


def get_wind_speed(soup):
    """ Extract the wind speed from the Rotowire game soup
    :param soup: Rotowire soup for the individual game
    :return: an integer representation of the wind speed (negative for "In", positive for "Out", zero otherwise)
    """
    wind_text = soup.find("div", {"class": WIND_LABEL}).text
    wind_words = wind_text.strip().split()
    if wind_words[len(wind_words)-1] == "Out":
        return int(wind_words[1])
    elif wind_words[len(wind_words)-1] == "In":
        return -1*int(wind_words[1])

    return 0


class UmpDataNotFound(Exception):

    def __init__(self):
        super(UmpDataNotFound, self).__init__("The ump data was not found in the soup")


def get_ump_name(soup):
    """ Extract the strikeouts per 9 innings for the ump for a given game
    :param soup: Rotowire soup for the individual game
    :return: float representation of the strikeouts per game
    """
    span15s = soup.findAll("div", {"class": "span15"})
    for span15 in span15s:
        node = span15.find("b")
        if node is not None:
            if node.text.strip() == "Ump:":
                ump_text = span15.text
                ump_words = ump_text.strip().split()
                if len(ump_words) >= 3:
                    return ump_words[1].strip() + " " + ump_words[2].strip()

    raise UmpDataNotFound


def get_ump_ks_per_game(soup):
    """ Extract the strikeouts per 9 innings for the ump for a given game
    :param soup: Rotowire soup for the individual game
    :return: float representation of the strikeouts per game
    """
    #TODO: move this to stat miner and lookup in database
    span15s = soup.findAll("div", {"class": "span15"})
    for span15 in span15s:
        node = span15.find("b")
        if node is not None:
            if node.text.strip() == "Ump:":
                ump_text = span15.text
                ump_words = ump_text.strip().split()
                for i in range(0, len(ump_words)):
                    if ump_words[i] == "K/9:":
                        return float(ump_words[i+1])

    raise UmpDataNotFound


def get_ump_runs_per_game(soup):
    """ Extract the strikeouts per 9 innings for the ump for a given game
    :param soup: Rotowire soup for the individual game
    :return: float representation of the strikeouts per game
    """
    span15s = soup.findAll("div", {"class": "span15"})
    for span15 in span15s:
        node = span15.find("b")
        if node is not None:
            if node.text.strip() == "Ump:":
                ump_text = span15.text
                ump_words = ump_text.strip().split()
                for i in range(0, len(ump_words)):
                    if ump_words[i] == "R/9:":
                        return float(ump_words[i+1].replace("&nbsp", ""))

    raise UmpDataNotFound


def get_game_matchups(url=None, game_date=None):

    if url is None:
        url = DAILY_LINEUPS_URL

    if game_date is None:
        game_date = date.today()

    soup = get_soup_from_url(url)

    header_nodes = soup.findAll("div", {"class": TEAM_REGION_LABEL})
    matchups = list()
    for header_node in header_nodes:
        matchup = GameMatchup()
        game_node = header_node.parent
        matchup.away_team = game_node.find("div", {"class": AWAY_TEAM_REGION_LABEL}).text.split()[0]
        matchup.home_team = game_node.find("div", {"class": HOME_TEAM_REGION_LABEL}).text.split()[0]
        game_time = game_node.find("div", {"class": TIME_REGION_LABEL}).find("a").text.replace("ET", "").strip()
        matchup.game_time = datetime.strptime(game_time, '%I:%M %p').strftime("%H:%M")
        matchup.game_date = str(game_date)
        try:
            pitchers = game_node.find("div", PITCHERS_REGION_LABEL).findAll("div")
            matchup.away_pitcher = get_pitcher(pitchers[0], matchup.away_team)
            matchup.home_pitcher = get_pitcher(pitchers[1], matchup.home_team)
        # No pitchers present on page
        except AttributeError:
            print "Game between %s and %s is not valid." % (matchup.away_team, matchup.home_team)
            continue

        matchups.append(matchup)

    return matchups
