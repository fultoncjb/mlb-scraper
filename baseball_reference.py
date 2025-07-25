"""
baseball_reference.py
Module used for scraping data from baseballreference.com
"""
import datetime

import bs4
import re
from enum import Enum
from time import sleep
import bidict

from beautiful_soup_helper import *
from datetime import date, timedelta

BASE_URL = "http://www.baseball-reference.com"
HITTER_RELEVANT_STAT_KEYS = ["G", "PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB", "CS", "BB", "SO", "TB",
                             "GDP", "HBP", "SH", "SF", "IBB"]


class Hand(Enum):
    LEFT = 1
    RIGHT = 2
    SWITCH = 3


class PlayerHandInformation(object):
    def __init__(self, bats: Hand, throws: Hand):
        self.bats = bats
        self.throws = throws


class BallparkFactors(object):
    def __init__(self, hitter: int, pitcher: int):
        self.hitter = hitter
        self.pitcher = pitcher


HAND_TRANSLATION_DICT = bidict.bidict(left=Hand.LEFT,
                                      right=Hand.RIGHT,
                                      both=Hand.SWITCH)


class PlayerIdentifier(object):
    def __init__(self, name: str, baseball_reference_id: str, team_abbrev: str):
        self._name = name
        self._baseball_reference_id = baseball_reference_id
        self._team_abbrev = team_abbrev

    def get_id(self) -> str:
        return self._baseball_reference_id

    def get_name(self) -> str:
        return self._name

    def get_last_name(self) -> str:
        return " ".join(self._name.split()[1:])

    def get_team(self) -> str:
        return self._team_abbrev


class HandedPlayerIdentifier(PlayerIdentifier):
    def __init__(self, name: str, baseball_reference_id: str, team_abbrev: str, bats: Hand, throws: Hand):
        super(HandedPlayerIdentifier, self).__init__(name, baseball_reference_id, team_abbrev)
        self._bats = bats
        self._throws = throws

    def get_bats(self) -> Hand:
        return self._bats

    def get_throws(self) -> Hand:
        return self._throws


def get_hitter_empty_stats() -> dict:
    return {key: 0.0 for key in HITTER_RELEVANT_STAT_KEYS}


def get_season_hitter_identifiers(year: int) -> [PlayerIdentifier]:
    """
    Given a year, get the name and Baseball Reference ID of all hitters that participated in that year
    :param year: year of interest
    :type year: int
    :param sleep_length: amount of time to sleep (in seconds) in between queries for a player's hand characteristics
    :type sleep_length: float
    :return: list of identifiers for a particular player
    :rtype: [PlayerIdentifier]
    """
    soup = get_hitter_soup(year)

    season_hitter_ids = list()

    try:
        hitter_table = soup.find("table", {"id": "players_standard_batting"})
        hitter_table = hitter_table.find("tbody")
        hitter_table_rows = hitter_table.findAll("tr")
    except AttributeError:
        return season_hitter_ids
    for hitter_table_row in hitter_table_rows:
        try:
            hitter_name_entry = hitter_table_row.find("td", {"data-stat": "name_display"}).find("a")
            hitter_name = hitter_name_entry.text.replace(u'\xa0', ' ')
            hitter_id = hitter_name_entry.get("href").split("/")
            hitter_id = str(hitter_id[len(hitter_id)-1]).replace(".shtml", "")
            team_entry = hitter_table_row.find("td", {"data-stat": "team_name_abbr"}).find("a")
            team_abbrev = team_entry.get("href").split("/")[2]

            season_hitter_ids.append(PlayerIdentifier(hitter_name, hitter_id, team_abbrev))
        except IndexError:
            continue
        except AttributeError:
            continue

    return season_hitter_ids


def append_hands_to_id(player_id: PlayerIdentifier) -> HandedPlayerIdentifier:
    bats_throws = get_bats_throws(player_id.get_id())
    return HandedPlayerIdentifier(player_id.get_name(), player_id.get_id(), player_id.get_team(),
                                  bats_throws.bats, bats_throws.throws)


def get_hitter_id(full_name, team, year=None, soup=None):
    """ Get the BaseballReference ID from the players name and team
    :param full_name: the full name of the player
    :param team: the BaseballReference team abbreviation
    :param year: an integer representing the year of interest (this is particularly useful because players may
    change teams (default is the current year)
    :param soup: BeautifulSoup object of all players in the given year
    :return: string representation of the player's BaseballReference ID
    """

    if year is None:
        year = date.today().year

    if soup is None:
        soup = get_hitter_soup(year)

    if soup is None:
        raise PlayerNameNotFound(full_name)
    try:
        hitter_table = soup.find("table", {"id": "players_standard_batting"})
        hitter_table = hitter_table.find("tbody")
        hitter_table_rows = hitter_table.findAll("tr")
    except AttributeError:
        raise PlayerNameNotFound(full_name)
    for hitter_table_row in hitter_table_rows:
        if hitter_table_row.get("class")[0] != "thead":
            try:
                hitter_entries = hitter_table_row.findAll("td")
                hitter_name_entry = hitter_entries[0].find("a")
                if hitter_name_entry.text.replace(u'\xa0', ' ') == full_name:
                    if team == hitter_entries[2].text:
                        hitter_id = hitter_name_entry.get("href").split("/")
                        return str(hitter_id[len(hitter_id)-1]).replace(".shtml", "")
            except IndexError:
                continue
            except AttributeError:
                continue

    raise PlayerNameNotFound(full_name)


def get_season_pitcher_identifiers(year: int, sleep_length: float = 10.0) -> [HandedPlayerIdentifier]:
    soup = get_pitcher_soup(year)

    season_pitcher_ids = list()

    try:
        pitcher_table = soup.find("table", {"id": "players_standard_pitching"})
        pitcher_table = pitcher_table.find("tbody")
        pitcher_table_rows = pitcher_table.findAll("tr")
    except AttributeError:
        return season_pitcher_ids
    for pitcher_table_row in pitcher_table_rows:
        if pitcher_table_row.get("class")[0] != "thead":
            try:
                pitcher_entries = pitcher_table_row.findAll("td")
                pitcher_name_entry = pitcher_entries[0].find("a")
                pitcher_name = pitcher_name_entry.text.replace(u'\xa0', ' ')
                pitcher_id = pitcher_name_entry.get("href").split("/")
                pitcher_id = str(pitcher_id[len(pitcher_id) - 1]).replace(".shtml", "")
                team_entry = pitcher_table_row.find("td", {"data-stat": "team_ID"}).find("a")
                team_abbrev = team_entry.get("href").split("/")[2]
                bats_throws = get_bats_throws(pitcher_id)
                sleep(sleep_length)
                season_pitcher_ids.append(HandedPlayerIdentifier(pitcher_name, pitcher_id, team_abbrev,
                                                                 bats_throws.bats, bats_throws.throws))
            except IndexError:
                continue
            except AttributeError:
                continue

    return season_pitcher_ids


def get_pitcher_id(full_name, team, year=None, soup=None):
    """ Get the BaseballReference ID from the players name and team
    :param full_name: the full name of the player
    :param team: the BaseballReference team abbreviation
    :param year: an integer representing the year of interest (this is particularly useful because players may
    change teams (default is the current year)
    :param soup: BeautifulSoup object of all players in the given year
    :return: string representation of the player's ID
    """

    if year is None:
        year = date.today().year

    if soup is None:
        soup = get_pitcher_soup(year)

    try:
        pitcher_table = soup.find("table", {"id": "players_standard_pitching"}).find("tbody")
        pitcher_table_rows = pitcher_table.findAll("tr")
    except AttributeError:
        raise PlayerNameNotFound(full_name)
    for pitcher_table_row in pitcher_table_rows:
        if pitcher_table_row.get("class")[0] != "thead":
            try:
                pitcher_entries = pitcher_table_row.findAll("td")
                pitcher_name_entry = pitcher_entries[0].find("a")
                if pitcher_name_entry.text.replace(u'\xa0', ' ') == full_name:
                    if team == pitcher_entries[2].text:
                        pitcher_id = pitcher_name_entry.get("href").split("/")
                        return str(pitcher_id[len(pitcher_id)-1]).replace(".shtml", "")
            except IndexError:
                continue
            except AttributeError:
                continue

    raise PlayerNameNotFound(full_name)


class PlayerNameNotFound(Exception):
    def __init__(self, name_str):
        super(PlayerNameNotFound, self).__init__("Player '%s' not found in the Baseball Reference page" % name_str)


def get_hitter_soup(year: int = None) -> bs4.BeautifulSoup:
    """
    :param year: integer representation of the year of interest (default is current year)
    :return: BeautifulSoup object of the home page for this hitter
    """
    if year is None:
        year = date.today().year

    hitter_year_url = BASE_URL + "/leagues/MLB/" + str(year) + "-standard-batting.shtml"
    return get_soup_from_url(hitter_year_url)


def get_pitcher_soup(year: int = None) -> bs4.BeautifulSoup:
    """
    :param year: integer representation of the year of interest (default is current year)
    :return: BeautifulSoup object of the home page for this pitcher
    """
    if year is None:
        year = date.today().year

    pitcher_year_url = BASE_URL + "/leagues/MLB/" + str(year) + "-standard-pitching.shtml"
    return get_comment_soup_from_url(pitcher_year_url)


class TableNotFound(Exception):
    def __init__(self, table_name):
        super(TableNotFound, self).__init__("Table '%s' not found in the Baseball Reference page" % table_name)


class TableRowNotFound(Exception):
    def __init__(self, table_row, table_column, table_name):
        super(TableRowNotFound, self).__init__("Table row '%s' not found in the column '%s' in the "
                                               "table %s in the Baseball Reference page" %
                                               (table_row, table_column, table_name))


class DidNotFacePitcher(Exception):
    def __init__(self, hitter_name, pitcher_name):
        super(DidNotFacePitcher, self).__init__("Player %s has never faced pitcher %s" % hitter_name, pitcher_name)


def get_vs_table_row_dict(soup, batter_id, pitcher_id):
    """ Special version of get_table_row_dict. Since Baseball Reference's batter vs. pitcher
    tables don't really have a standardized row name, we have to just count the number of rows and
    accumulate the stats.
    :param soup: BeautifulSoup object containing the table HTML
    :param batter_id: the Baseball Reference ID of the relevant batter
    :param pitcher_id: the Baseball Reference ID of the relevant pitcher
    :return: a dictionary representing the stats
    """
    # Note: we seem to need BASE_URL as a prefix during unit tests
    batter_vs_pitcher_base = "/baseball/batter_vs_pitcher.cgi?batter="

    try:
        results_table = soup.find("table", {"id": "result_table"})
        table_header_list = results_table.find("thead").findAll("th")
        table_header_list = [x.text for x in table_header_list]
        table_body = results_table.find("tbody")
    except AttributeError:
        raise TableNotFound("ajax_result_table")

    matching_url = batter_vs_pitcher_base + batter_id + "&pitcher=" + pitcher_id + "&post=0"
    try:
        stat_row = table_body.find("a", {"href": matching_url}).parent.parent
    except AttributeError:
        raise TableRowNotFound(matching_url, "NULL", "ajax_result_table")

    # Create a dictionary of the stat attributes
    stat_dict = dict()
    stat_entries = stat_row.findAll("td")
    # The names are now labeled as "th"
    if len(stat_entries)+1 != len(table_header_list):
        raise TableRowNotFound(matching_url, "NULL", "ajax_result_table")
    for i in range(0, len(stat_entries)):
        if stat_entries[i].text == "":
            stat_dict[table_header_list[i+1]] = 0
        else:
            stat_dict[table_header_list[i+1]] = stat_entries[i].text.replace(u"\xa0", " ")

    return stat_dict


def get_all_table_row_dicts(soup: bs4.BeautifulSoup, table_name: str) -> (list, [dict]):
    """
    Get the column header labels as well as all rows in a given table in the given BeautifulSoup object
    :param soup: BeautifulSoup object containing the table_name table as a child
    :type soup: bs4.BeautifulSoup
    :param table_name: name of the table of interest
    :type table_name: str
    :return: list of dictionaries of all rows in a given table
    :rtype: [dict]
    """
    results_table = soup.find("table", {"id": table_name})
    if results_table is None:
        raise TableNotFound(table_name)

    table_header_list = results_table.find("thead").findAll("th")
    table_header_list = [x.text for x in table_header_list]
    stat_rows = results_table.findAll("tr")

    stat_dict_list = list()
    for stat_row in stat_rows:
        # Create a dictionary of the stat attributes
        stat_dict = dict()
        stat_entries = stat_row.findAll(["th", "td"])
        # The dictionary does not have valid entries, move on to the next row
        if len(stat_entries) != len(table_header_list):
            continue
        for i in range(1, len(stat_entries)):
            if stat_entries[i].text == "" or stat_entries[i].name != "td":
                stat_dict[table_header_list[i]] = 0
            else:
                stat_dict[table_header_list[i]] = stat_entries[i].text.replace(u"\xa0", " ")
        stat_dict_list.append(stat_dict)

    return table_header_list, stat_dict_list


def get_table_row_dict(soup, table_name, table_row_label, table_column_label):
    """ Get a dictionary representation of a Baseball Reference table of stats
    :param soup: BeautifulSoup object containing the table HTML
    :param table_name: HTML "id" tag for the table
    :param table_row_label: bare text label for the row of interest
    :param table_column_label: bare text label for the column of interest
    :return: a dictionary representing the stats
    """

    try:
        table_header_list, stat_dicts = get_all_table_row_dicts(soup, table_name)
    except AttributeError:
        raise TableRowNotFound(table_row_label, table_column_label, table_name)

    for stat_dict in stat_dicts:
        try:
            if stat_dict[table_column_label] == table_row_label:
                return stat_dict
        except KeyError:
            raise TableRowNotFound(table_row_label, table_column_label, table_name)

    raise TableRowNotFound(table_row_label, table_column_label, table_name)


def get_table_body_row_dict(soup, table_name, table_row_label, table_column_label):
    """ Get a dictionary representation of a Baseball Reference table of stats
    :param soup: BeautifulSoup object containing the table HTML
    :param table_name: HTML "id" tag for the table
    :param table_row_label: bare text label for the row of interest
    :param table_column_label: bare text label for the column of interest
    :return: a dictionary representing the stats
    """
    results_table = soup.find("table", {"id": table_name})
    if results_table is None:
        raise TableNotFound(table_name)

    try:
        table_header_list = results_table.find("thead").findAll("th")
    except AttributeError:
        raise TableRowNotFound(table_row_label, table_column_label, table_name)
    table_header_list = [x.text for x in table_header_list]
    stat_rows = results_table.findAll("tr")

    for stat_row in stat_rows:
        # Create a dictionary of the stat attributes
        stat_dict = dict()
        stat_entries = stat_row.findAll(["th", "td"])
        # The dictionary does not have valid entries, move on to the next row
        if len(stat_entries) != len(table_header_list):
            continue
        for i in range(0, len(stat_entries)):
            if stat_entries[i].text == "":
                stat_dict[table_header_list[i]] = 0
            else:
                stat_dict[table_header_list[i]] = stat_entries[i].text.replace(u"\xa0", " ")
        try:
            if stat_dict[table_column_label] == table_row_label:
                return stat_dict
        except KeyError:
            raise TableRowNotFound(table_row_label, table_column_label, table_name)

    raise TableRowNotFound(table_row_label, table_column_label, table_name)


def get_career_regular_season_hitting_soup(hitter_id: str) -> BeautifulSoup:
    url = BASE_URL + "/players/" + hitter_id[0] + "/" + str(hitter_id) + ".shtml"
    return get_soup_from_url(url)


def get_career_postseason_hitting_soup(hitter_id: str) -> BeautifulSoup:
    url = BASE_URL + "/players/" + hitter_id[0] + "/" + str(hitter_id) + ".shtml"
    return get_comment_soup_from_url(url)


def get_hitting_stats_table(soup: BeautifulSoup, table_id: str) -> dict:
    results_table = soup.find("table", {"id": table_id})
    if results_table is None:
        raise TableNotFound(table_id)

    table_footer = results_table.find("tfoot")
    if table_footer is None:
        raise TableNotFound(table_id)

    table_header = results_table.find("thead")
    if table_header is None:
        raise TableNotFound(table_id)

    career_row_header = table_footer.find("th", {"data-stat": "player_stats_summary_explain"})

    # If there is no data, then return zeros for all categories
    if career_row_header is None:
        return get_hitter_empty_stats()

    career_row = career_row_header.parent
    column_span = int(career_row_header["colspan"])
    stat_labels = [x.text for x in table_header.findAll("th")[column_span:-2]]
    stat_values = [x.text for x in career_row.findAll("td")[:-2]]

    stat_dict = dict()
    for idx in range(0, len(stat_labels)):
        if stat_values[idx] == "":
            stat_dict[stat_labels[idx]] = 0
        else:
            stat_dict[stat_labels[idx]] = stat_values[idx]

    return stat_dict


def get_career_regular_season_hitting_stats(baseball_reference_id, soup=None):
    """ Get a dictionary representation of the hitter stats for the given hitter id
    :param baseball_reference_id: unique BaseballReference ID for this hitter
    :param soup: BeautifulSoup object of the hitter career stats page (default is the URL for the given hitter)
    :return: dictionary representation of the hitter's stat home page
    """
    if soup is None:
        soup = get_career_regular_season_hitting_soup(baseball_reference_id)

    return get_hitting_stats_table(soup, "batting_standard")


def get_career_postseason_hitting_stats(hitter_id: str, soup=None):
    if soup is None:
        soup = get_career_postseason_hitting_soup(hitter_id)

    return get_hitting_stats_table(soup, "batting_postseason")


def get_career_hitting_stats(baseball_reference_id: str, soup: BeautifulSoup = None) -> dict:
    reg_season_stat_dict = get_career_regular_season_hitting_stats(baseball_reference_id)
    playoff_stat_dict = get_career_postseason_hitting_stats(baseball_reference_id)

    return {label: int(reg_season_stat_dict[label]) + int(playoff_stat_dict[label]) for label in HITTER_RELEVANT_STAT_KEYS}


def get_vs_hand_hitting_stats(baseball_reference_id, hand_value, soup=None):
    """ Get a dictionary representation of the hitter stats against the given pitcher hand
    :param baseball_reference_id: BaseballReference unique ID for this hitter
    :param hand_value: "L" for left, "R" for right
    :param soup: BeautifulSoup object of the hitter career stats page (default is the URL for the given hitter)
    :return: dictionary representation of the hitter's stat home page
    """
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=b"
        soup = get_comment_soup_from_url(url)

    if hand_value == "L":
        hand = "vs LHP"
    elif hand_value == "R":
        hand = "vs RHP"
    else:
        print("Invalid hand enum %s." % hand_value)
        return None

    return get_table_row_dict(soup, "plato", hand, "Split")


def get_recent_hitting_stats(baseball_reference_id, soup=None):
    """ Get a dictionary representation of the hitter's stats from the last 7 days
    :param baseball_reference_id: BaseballReference unique ID for this hitter
    :param soup: BeautifulSoup object of the hitter's stat home page (default is the URL for the given hitter)
    :return: dictionary representation of the hitter's stats
    """
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=b"
        soup = get_comment_soup_from_url(url)

    return get_table_row_dict(soup, "total", "Last 7 days", "Split")


def get_season_hitting_stats(baseball_reference_id, year=None, soup=None):
    """ Get a dictionary representation of the hitter's stats for the current season
    :param baseball_reference_id: BaseballReference unique ID for the given hitter
    :param year: integer representation of the year of interest (default is current year)
    :param soup: BeautifulSoup representation of the hitter's stat home page (default is the URL for the given hitter)
    :return: dictionary representation of the hitter's stats
    """
    if year is None:
        year = date.today().year
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=" + str(year) + "&t=b"
        print(url)
        soup = get_comment_soup_from_url(url)

    return get_table_body_row_dict(soup, "total", str(year) + " Totals", "Split")


def get_vs_pitcher_stats(batter_id, pitcher_id, soup=None):
    """ Get a dictionary representation of the hitter's stats against the given pitcher
    :param batter_id: BaseballReference unique ID for the hitter of interest
    :param pitcher_id: BaseballReference unique ID for the pitcher of interest
    :param soup: BeautifulSoup representation of the hitter's vs. pitcher home page (default is the URL for the given hitter)
    :return: dictionary representation of the hitter's stats
    """
    if soup is None:
        url = "https://stathead.com/baseball/batter_vs_pitcher.cgi?batter=" + str(batter_id) + "&utm_medium=br&utm_source=player-finder-links&utm_campaign=baseball"
        print(url)
        soup = get_soup_from_url(url)

    return get_vs_table_row_dict(soup, batter_id, pitcher_id)


def get_hitter_page_career_soup(baseball_reference_id):
    """ Get the BeautifulSoup object for the hitter stat home page
    :param baseball_reference_id: BaseballReference unique ID for the hitter of interest
    :return: BeautifulSoup for the hitter stat home page
    """
    return get_comment_soup_from_url(BASE_URL + "/players/split.fcgi?id=" +
                                                 str(baseball_reference_id) + "&year=Career&t=b")


def get_career_pitching_stats(baseball_reference_id, soup=None):
    """ Get a dictionary representation of the career stats for the given pitcher
    :param baseball_reference_id: BaseballReference unique ID for the pitcher of interest
    :param soup: BeautifulSoup object of the pitcher's stat home page
    :return: dictionary representation of the career stats
    """
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=p"
        soup = get_comment_soup_from_url(url)

    return get_table_row_dict(soup, "total_extra", "Career Totals", "Split")


def get_pitcher_page_career_soup(baseball_reference_id):
    """ Get the career stats for the given pitcher
    :param baseball_reference_id: BaseballReference ID of the pitcher of interest
    :return: BeautifulSoup object of the pitcher's stat home page
    """
    url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=p"
    print(url)
    return get_comment_soup_from_url(url)


def get_season_pitcher_stats(baseball_reference_id, year=None, soup=None):
    """ Get the season stats for the given pitcher
    :param baseball_reference_id: BaseballReference unique ID for the pitcher of interest
    :param year: integer representation of the year
    :param soup: BeautifulSoup of the stat page for the given year (default is the URL for this year)
    :return: dictionary representation of the pitcher's season stats
    """
    if year is None:
        year = date.today().year
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=" + str(year) + "&t=p"
        print(url)
        soup = get_comment_soup_from_url(url)

    return get_table_body_row_dict(soup, "total_extra", str(year) + " Totals", "Split")


def get_recent_pitcher_stats(baseball_reference_id, soup=None):
    """ Get a dictionary representation of the pitcher stats for the last 14 days
    :param baseball_reference_id: BaseballReference unique ID for the pitcher of interest
    :param soup: BeautifulSoup object of the pitcher's stat home page (default is the URL for the given ID)
    :return: dictionary representation of the pitcher stats
    """
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=p"
        soup = get_comment_soup_from_url(url)

    try:
        table_row_dict = get_table_row_dict(soup, "total_extra", "Last 14 days", "Split")
    except TableRowNotFound:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=p"
        table_row_dict = get_table_row_dict(get_comment_soup_from_url(url), "total_extra", "Last 14 days", "Split")

    return table_row_dict


def get_season_hitting_game_logs(baseball_reference_id: str, year: int) -> (dict, [dict]):
    """
    Get the hitting game logs for an entire season for a given player
    :param baseball_reference_id: BaseballReference ID for a particular player
    :type baseball_reference_id: str
    :param year: year of interest
    :type year: int
    :return: column header labels as well as all rows in the hitting game log table
    :rtype: (dict, [dict])
    """
    url = BASE_URL + "/players/gl.fcgi?id=" + str(baseball_reference_id) + "&t=b&year=" + str(year)
    soup = get_soup_from_url(url)
    return get_all_table_row_dicts(soup, "batting_gamelogs")


def get_hitting_game_log(baseball_reference_id, soup=None, game_date=None):
    """ Get a dictionary representation of hitting stats for a particular player on a particular day
    :param baseball_reference_id: BaseballReference unique ID for the hitter of interest
    :param soup: BeautifulSoup object of the hitter game log (default is the URL for the game log of the given ID)
    :param game_date: date of the game of interest (default is today)
    :return: dictionary representation of the game log stats
    """
    if game_date is None:
        game_date = date.today()
    if soup is None:
        url = BASE_URL + "/players/gl.fcgi?id=" + str(baseball_reference_id) + "&t=b&year=" + str(game_date.year)
        soup = get_soup_from_url(url)
    try:
        return get_table_row_dict(soup, "batting_gamelogs", date_abbreviations[game_date.month] + " " +
                                  str(game_date.day), "Date")
    except TableNotFound as e:
        print(e)
        return None
    except TableRowNotFound as e1:
        print(e1)
        return None


def get_season_pitching_game_logs(baseball_reference_id: str, year: int) -> (dict, [dict]):
    url = BASE_URL + "/players/gl.fcgi?id=" + str(baseball_reference_id) + "&t=p&year=" + str(year)
    soup = get_soup_from_url(url)
    return get_all_table_row_dicts(soup, "pitching_gamelogs")


def get_pitching_game_log(baseball_reference_id, soup=None, game_date=None):
    """ Get a dictionary representation of the game log stats from the given date
    :param baseball_reference_id: BaseballReference unique ID for the pitcher of interest
    :param soup: BeautifulSoup object of the pitcher game log (default is the URL for the game log of the given ID)
    :param game_date: the game date of interest (in format yyyy-mm-dd)
    :return: dictionary representation of the game log stats
    """
    if game_date is None:
        game_date = date.today()
    if soup is None:
        url = BASE_URL + "/players/gl.fcgi?id=" + str(baseball_reference_id) + "&t=p&year=" + str(game_date.year)
        soup = get_soup_from_url(url)
    try:
        return get_table_row_dict(soup, "pitching_gamelogs", date_abbreviations[game_date.month] + " " +
                                  str(game_date.day), "Date")
    except TableNotFound as e:
        print(e)
        return None
    except TableRowNotFound as e1:
        print(e1)
        return None


def get_team_info(team_name, year_of_interest=None, team_soup=None):
    """ Get the BaseballReference hitter/pitcher factors for the given team
    :param team_name: name of the team of interest
    :param year_of_interest: integer representation of the year of interest
    :param team_soup: BeautifulSoup object for the team information page
    :return: hitter factor, pitcher factor tuple for the given team
    """
    url = "/about/parkadjust.shtml"

    team_abbreviation = team_name

    if year_of_interest is None:
        year_of_interest = date.today().year

    if team_soup is None:
        url = BASE_URL + "/teams/" + team_abbreviation + "/" + str(year_of_interest) + ".shtml"
        team_soup = get_soup_from_url(url)

    try:
        sub_nodes = team_soup.find("a", {"href": url}).parent.parent.findAll("strong")
    except AttributeError:
        return None, None
    for sub_node in sub_nodes:
        for content in sub_node.contents:
            if content is not None:
                try:
                    if "multi-year:" in content.lower():
                        factor_string = sub_node.next_sibling.split(",")

                        hitter_factor = int(factor_string[0].split("-")[1].strip().split(" ")[0])
                        pitcher_factor = int(factor_string[1].split("-")[1].strip().split(" ")[0])

                        return hitter_factor, pitcher_factor
                except TypeError:
                    continue

    return None, None


def get_bats_throws(baseball_reference_id: str) -> PlayerHandInformation:
    url = BASE_URL + "/players/" + baseball_reference_id[0] + "/" + baseball_reference_id + ".shtml"
    player_soup = get_soup_from_url(url)
    player_info = player_soup.find("div", {"id": "info"}).find("div", {"id": "meta"}).findAll("div")[-1]
    strong_entries = player_info.findAll("strong")
    bats_text = None
    throws_text = None
    for strong_entry in strong_entries:
        tag_text = strong_entry.text.strip().replace("\n", "").replace("\t", "").replace(" ", "")
        if tag_text == "Bats:":
            bats_text = strong_entry.next_sibling.replace("\n", "").replace("\t", "").replace(" ", "").replace("\u2022", "").strip().lower()
        elif tag_text == "Throws:":
            throws_text = strong_entry.next_sibling.replace("\n", "").replace("\t", "").replace(" ", "").replace("\u2022", "").strip().lower()

    if bats_text is None or throws_text is None:
        raise TableNotFound("bats-throws")

    return PlayerHandInformation(bats=HAND_TRANSLATION_DICT[bats_text], throws=HAND_TRANSLATION_DICT[throws_text])


def get_ballpack_factors(team: str, year: int) -> BallparkFactors:
    url = BASE_URL + "/teams/" + team + "/" + str(year) + ".shtml"
    team_soup = get_soup_from_url(url)
    try:
        team_metadata = team_soup.find("div", {"data-template": "Partials/Teams/Summary"}).findAll("strong")
        for strong_entry in team_metadata:
            if strong_entry.text == "Multi-year:":
                batting_pitching = strong_entry.next_sibling.strip().replace("\n", "")
                re_match = re.match("Batting - ([0-9]*), Pitching - ([0-9]*)", batting_pitching)
                return BallparkFactors(hitter=int(re_match.group(1)), pitcher=int(re_match.group(2)))
    except AttributeError:
        print("Could not find team %s ballpark factor for year %i" % (team, year))
        pass

    raise TableNotFound("ballpark-factors")


def get_stathead_id(baseball_reference_id: str) -> str:
    url = BASE_URL + "/players/" + baseball_reference_id[0] + "/" + baseball_reference_id + ".shtml"
    player_soup = get_soup_from_url(url)
    span_list = player_soup.find("div", {"id": "inner_nav"}).findAll("span")
    for span in span_list:
        if "Finders & Advanced Stats" in span.text:
            for link in span.parent.find("div").find("ul").findAll("li"):
                if "vs. Pitcher" in link.text or "vs. Batter" in link.text:
                    link_text = link.find("a").get("href")
                    re_match = re.match(".*&player_id1=([a-zA-Z0-9-.]*)&", link_text)
                    return re_match.group(1)

