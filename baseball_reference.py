"""
baseball_reference.py
Module used for scraping data from baseballreference.com
"""

from beautiful_soup_helper import *
from datetime import date, timedelta


BASE_URL = "http://www.baseball-reference.com"


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


def get_hitter_soup(year=None):
    """
    :param year: integer representation of the year of interest (default is current year)
    :return: BeautifulSoup object of the home page for this hitter
    """
    if year is None:
        year = date.today().year

    hitter_year_url = BASE_URL + "/leagues/MLB/" + str(year) + "-standard-batting.shtml"
    return get_comment_soup_from_url(hitter_year_url)


def get_pitcher_soup(year=None):
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


def get_table_row_dict(soup, table_name, table_row_label, table_column_label):
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
        for i in range(1, len(stat_entries)):
            if stat_entries[i].text == "" or stat_entries[i].name != "td":
                stat_dict[table_header_list[i]] = 0
            else:
                stat_dict[table_header_list[i]] = stat_entries[i].text.replace(u"\xa0", " ")
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


def get_career_hitting_stats(baseball_reference_id, soup=None):
    """ Get a dictionary representation of the hitter stats for the given hitter id
    :param baseball_reference_id: unique BaseballReference ID for this hitter
    :param soup: BeautifulSoup object of the hitter career stats page (default is the URL for the given hitter)
    :return: dictionary representation of the hitter's stat home page
    """
    if soup is None:
        url = BASE_URL + "/players/split.fcgi?id=" + str(baseball_reference_id) + "&year=Career&t=b"
        soup = get_comment_soup_from_url(url)

    return get_table_row_dict(soup, "total", "Career Totals", "Split")


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


def get_hitting_game_log(baseball_reference_id, soup=None, game_date=None):
    """ Get a dictionary representation of yesterday's game log stats
    :param baseball_reference_id: BaseballReference unique ID for the hitter of interest
    :param soup: BeautifulSoup object of the hitter game log (default is the URL for the game log of the given ID)
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
    # TODO: just try again for now, explore BeautifulSoup built-in options for this
    except TableNotFound as e:
        print(e)
        return None
    except TableRowNotFound as e1:
        print(e1)
        return None


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

date_abbreviations = {1: "Jan",
                      2: "Feb",
                      3: "Mar",
                      4: "Apr",
                      5: "May",
                      6: "Jun",
                      7: "Jul",
                      8: "Aug",
                      9: "Sep",
                      10: "Oct",
                      11: "Nov",
                      12: "Dec"}
