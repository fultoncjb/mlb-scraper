"""
rotowire.py
Module used for scraping data from rotowire.com
"""

from datetime import datetime, date

import bs4
import selenium.webdriver.remote.webelement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from team_dict import *
from baseball_reference import get_team_info, TableNotFound
from beautiful_soup_helper import get_soup_from_url

# Daily lineups relevant HTML labels
DAILY_LINEUPS_URL = "https://www.rotowire.com/baseball/daily-lineups.php"
GAME_REGION_LABEL = "offset1 span15"
LINEUP_LABEL = "lineup.is-mlb"
TEAM_REGION_LABEL = "lineup__main"
AWAY_TEAM_REGION_LABEL = "lineup__list is-visit"
HOME_TEAM_REGION_LABEL = "lineup__list is-home"
GAME_INFO_LABEL = "dlineups-topboxcenter"
TIME_REGION_LABEL = "dlineups-topboxcenter-topline"
AWAY_TEAM_PLAYER_LABEL = "lineup__player"
HOME_TEAM_PLAYER_LABEL = AWAY_TEAM_PLAYER_LABEL
LINEUPS_CLASS_LABEL = "lineup__box"
POSITION_CLASS_LABEL = "lineup__pos"
PITCHERS_REGION_LABEL = "span11 dlineups-pitchers"
HAND_CLASS_LABEL = "lineup__bats"
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
    def __init__(self, team: str, rotowire_id: str, position: str, hand: str, name: str, dfs_salary: int):
        self.team = team
        self.rotowire_id = rotowire_id
        self.position = position
        self.hand = hand
        self.name = name
        self.dfs_salary = dfs_salary

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


class SeleniumRotowireMiner(object):
    """
    Class used to mine data for upcoming games using Selenium so that it may manipulate the page to get
    all the necessary data.
    """

    def get_game_lineups(self, url: str = None, game_date: date = None) -> [Game]:
        """
        Get the list of Game objects representing all players participating in the games from the input url and date
        :param url: URL to open with Selenium containing the daily lineups (default is the daily linueps page from today)
        :type url: str
        :param game_date: date of the game (default is today)
        :type game_date: date
        :return: list of Game objects
        :rtype: [Game]
        """

        if url is None:
            url = DAILY_LINEUPS_URL

        if game_date is None:
            game_date = date.today()

        # Open the page and show the Draftkings salaries
        browser = webdriver.Firefox()
        browser.get(url)

        # Close promotional modal
        # TODO need a way of trying this and moving on if it doesn't exist after a certain amount of time
        try:
            modal_dismiss_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, "close-vwo-ps-modal")))
            modal_dismiss_button.click()
        except selenium.common.exceptions.TimeoutException:
            print("Did not encounter pop-up modal. Proceeding...")

        main_node = browser.find_element(By.TAG_NAME, "main").find_element(By.XPATH, ".//div[@class='flex-row flex-wrap mb-10']")
        dfs_show_salaries_node = main_node.find_element(By.XPATH, ".//div[@data-name='lineups-mlb-showsalaries']")
        # TODO this isn't necessarily correct because this won't be the class name if the
        dfs_yes_button = WebDriverWait(dfs_show_salaries_node, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "toggle-tab")))
        dfs_yes_button.click()
        # TODO may also want to click the button determining whether the started games are hidden or not
        # show_display_settings_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "revealer btn soft size-1 pad-2")))
        # show_display_settings_button.click()

        lineup_nodes = browser.find_elements(By.CLASS_NAME, LINEUP_LABEL)
        games = list()
        for lineup_node in lineup_nodes:
            home_team_lineup = list()
            away_team_lineup = list()
            try:
                lineup_top = lineup_node.find_element(By.CLASS_NAME, "lineup__top")
                away_team_abbreviation = lineup_top.find_element(By.XPATH, ".//div[@class='lineup__team is-visit']").find_element(By.XPATH, ".//div[@class='lineup__abbr']").get_attribute("innerHTML")
                home_team_abbreviation = lineup_top.find_element(By.XPATH, ".//div[@class='lineup__team is-home']").find_element(By.XPATH, ".//div[@class='lineup__abbr']").get_attribute("innerHTML")
                game_time = lineup_node.find_element(By.CLASS_NAME, "lineup__time").text.replace("ET", "").strip()
                if len(game_time) == 0:
                    print("WARNING: game date could not be parsed! Ignoring game between " + away_team_abbreviation + " and " + home_team_abbreviation)
                    continue

                game_time = datetime.strptime(game_time, '%I:%M %p').strftime("%H:%M")

                main_game_node = lineup_node.find_element(By.CLASS_NAME, "lineup__main")
                away_lineup_node = main_game_node.find_element(By.XPATH, ".//ul[@class='lineup__list is-visit']")
                home_lineup_node = main_game_node.find_element(By.XPATH, ".//ul[@class='lineup__list is-home']")

                # Get the data on the away lineup with DFS salaries
                # salary_idx = 0
                # away_lineup_salaries = away_lineup_node.find_elements(By.CLASS_NAME, "salaries")
                away_players = away_lineup_node.find_elements(By.CLASS_NAME, AWAY_TEAM_PLAYER_LABEL)
                # TODO for some reason, Rotowire doesn't render some of the games, so the DFS salaries are not available
                # if len(away_players) != len(away_lineup_salaries):
                #     print("There are no DFS salaries for matchup " + away_team_abbreviation + " at " + home_team_abbreviation)
                #     continue
                for away_player in away_players:
                    # salary = int(away_lineup_salaries[salary_idx].text.replace('$', '').replace(',', ''))
                    # salary_idx += 1
                    away_team_lineup.append(self.get_hitter(away_player, away_team_abbreviation, 0))
                    # away_team_lineup.append(self.get_hitter(away_player, away_team_abbreviation, salary))

                # Get the data on the home lineup with DFS salaries
                # salary_idx = 0
                # home_lineup_salaries = home_lineup_node.find_elements(By.CLASS_NAME, "salaries")
                home_players = home_lineup_node.find_elements(By.CLASS_NAME, HOME_TEAM_PLAYER_LABEL)
                for home_player in home_players:
                    # salary = int(home_lineup_salaries[salary_idx].text.replace('$', '').replace(',', ''))
                    # salary_idx += 1
                    home_team_lineup.append(self.get_hitter(home_player, home_team_abbreviation, 0))
                    # home_team_lineup.append(self.get_hitter(home_player, home_team_abbreviation, salary))

                # Get the data on the pitchers
                away_pitcher = away_lineup_node.find_element(By.CLASS_NAME, "lineup__player-highlight-name")
                away_team_pitcher = self.get_pitcher(away_pitcher, away_team_abbreviation, 0)
                home_pitcher = home_lineup_node.find_element(By.CLASS_NAME, "lineup__player-highlight-name")
                home_team_pitcher = self.get_pitcher(home_pitcher, home_team_abbreviation, 0)

                current_game = Game(away_team_lineup, away_team_pitcher, home_team_lineup, home_team_pitcher,
                                    str(game_date), str(game_time))

                games.append(current_game)
            except NoSuchElementException:
                continue

        return games

    @staticmethod
    def get_id(web_element_node: selenium.webdriver.remote.webelement.WebElement) -> str:
        """
        Get the player's unique Rotowire ID
        :param web_element_node: input element node containing the player data in a lineup
        :type web_element_node: selenium.webdriver.remote.webelement.WebElement
        :return: string representation of the player's Rotowire ID
        :rtype: str
        """
        return web_element_node.find_element(By.TAG_NAME, "a").get_attribute("href").split("/")[-1].split("-")[-1]

    @staticmethod
    def get_hand_bats(web_element_node: selenium.webdriver.remote.webelement.WebElement) -> str:
        """
        Get the side of the plate the player hits from ("L" "R" or "S")
        :param web_element_node: input element node containing the player data in a lineup
        :type web_element_node: selenium.webdriver.remote.webelement.WebElement
        :return: string representation of the side of the plate the player hits from
        :rtype: str
        """
        return web_element_node.find_element(By.CLASS_NAME, "lineup__bats").text

    @staticmethod
    def get_hand_throws(web_element_node: selenium.webdriver.remote.webelement.WebElement) -> str:
        """
        Get the hand the player uses to throw with ("L" or "R")
        :param web_element_node: input element node containing the player data in a lineup
        :type web_element_node: selenium.webdriver.remote.webelement.WebElement
        :return: string representation of the hand the player throws with
        :rtype: str
        """
        return web_element_node.find_element(By.CLASS_NAME, "lineup__throws").text

    def get_hitter(self, web_element_node: selenium.webdriver.remote.webelement.WebElement,
                   team: str, dfs_salary: int) -> PlayerStruct:
        """
        Aggregate the incoming information about the hitter into a unified structure
        :param web_element_node: input element node containing the player data in a lineup
        :type web_element_node: selenium.webdriver.remote.webelement.WebElement
        :param team: string abbreviation for the team the player is on
        :type team: str
        :param dfs_salary: salary the player would theoretically make in a Draftkings contest
        :type dfs_salary: int
        :return: aggregate PlayerStruct object of all preliminary information about the hitter
        :rtype: PlayerStruct
        """
        rotowire_id = self.get_id(web_element_node)
        name = web_element_node.find_element(By.TAG_NAME, "a").get_attribute("title")
        position = web_element_node.find_element(By.CLASS_NAME, POSITION_CLASS_LABEL).text
        hand = self.get_hand_bats(web_element_node)

        return PlayerStruct(team, rotowire_id, position, hand, name, dfs_salary)

    def get_pitcher(self, web_element_node: selenium.webdriver.remote.webelement.WebElement, team: str,
                    dfs_salary: int):
        """
        Aggregate the incoming information about the pitcher into a unified structure
        :param web_element_node: input element node containing the player data in a lineup
        :type web_element_node: selenium.webdriver.remote.webelement.WebElement
        :param team: string abbreviation for the team the player is on
        :type team: str
        :param dfs_salary: salary the player would theoretically make in a Draftkings contest
        :type dfs_salary: int
        :return: aggregate PlayerStruct object of all preliminary information about the pitcher
        :rtype: PlayerStruct
        """
        rotowire_id = self.get_id(web_element_node)
        hand = self.get_hand_throws(web_element_node)
        name = web_element_node.find_element(By.TAG_NAME, "a").text

        return PlayerStruct(team, rotowire_id, "P", hand, name, dfs_salary)


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
        away_team_abbreviation = "UNKNOWN"
        home_team_abbreviation = "UNKNOWN"
        try:
            top_soup = game_node.find("div", {"class": "lineup__top"})
            away_team_abbreviation = top_soup.find("div", {"class": "lineup__team is-visit"}).find("div", {"class": "lineup__abbr"}).text
            home_team_abbreviation = top_soup.find("div", {"class": "lineup__team is-home"}).find("div", {"class": "lineup__abbr"}).text
            game_time = game_node.parent.find("div", {"class": "lineup__time"}).text.replace("ET", "").strip()
            game_time = datetime.strptime(game_time, '%I:%M %p').strftime("%H:%M")

            main_game_node = game_node.find("div", {"class": "lineup__main"})
            away_lineup_node = main_game_node.find("ul", {"class": "lineup__list is-visit"})
            home_lineup_node = main_game_node.find("ul", {"class": "lineup__list is-home"})

            # TODO the salaries are not enabled by default, so we must use selenium to push the correct buttons
            salary_idx = 0
            away_lineup_salaries = away_lineup_node.findAll("li", {"class": "salaries"})
            for away_player in away_lineup_node.findAll("li", {"class": AWAY_TEAM_PLAYER_LABEL}):
                salary = away_lineup_salaries[salary_idx].text
                salary_idx += 1
                away_team_lineup.append(get_hitter(away_player, away_team_abbreviation, salary))

            salary_idx = 0
            home_lineup_salaries = home_lineup_node.findAll("li", {"class": "salaries"})
            for home_player in home_lineup_node.findAll("li", {"class": HOME_TEAM_PLAYER_LABEL}):
                salary = home_lineup_salaries[salary_idx].text
                salary_idx += 1
                home_team_lineup.append(get_hitter(home_player, home_team_abbreviation, salary))

            away_pitcher = away_lineup_node.find("div", {"class": "lineup__player-highlight-name"})
            away_team_pitcher = get_pitcher(away_pitcher, away_team_abbreviation)
            home_pitcher = home_lineup_node.find("div", {"class": "lineup__player-highlight-name"})
            home_team_pitcher = get_pitcher(home_pitcher, home_team_abbreviation)
        # No pitchers present on page
        except AttributeError:
            print("Game between %s and %s is not valid." % (away_team_abbreviation, home_team_abbreviation))
            continue

        current_game = Game(away_team_lineup, away_team_pitcher, home_team_lineup, home_team_pitcher, str(game_date), str(game_time))

        if current_game.is_valid():
            game_factors = get_external_game_factors(game_node, home_team_abbreviation)
            # TODO figure out if we can just not populate these fields
            if game_factors is not None:
                current_game.wind_speed = game_factors.wind_speed
                current_game.umpire_name = game_factors.ump_name
            else:
                current_game.wind_speed = 0
                current_game.umpire_name = "Unknown"
            games.append(current_game)
        else:
            print("Game between %s and %s is not valid." % (away_team_abbreviation, home_team_abbreviation))

    return games


def get_external_game_factors(game_node, home_team_abbreviation):
    """
    :param game_node: BeautifulSoup object containing the game from the daily lineups page
    :return: a GameEntry containing the
    """
    try:
        extra_node = game_node.find("div", {"class": "lineup__extra"})
        weather_node = extra_node.find("div", {"class": "lineup__weather"}).find("div",
                                                                                 {"class": "lineup__weather-text"})
        wind_speed = get_wind_speed(weather_node)
        temperature = get_temperature(weather_node)
        """TODO: add temperature
        For now, we will use nominal temperature and umpire readings
        """
        ump_name = None
        try:
            ump_name = get_ump_name(game_node)
        except UmpDataNotFound:
            print("Ump data not found.")
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


def get_hitter(soup: bs4.BeautifulSoup, team: str, dfs_salary: int):
    """ Get a PlayerStruct representing a hitter
    If a database session is not provided, open the player page to obtain the hitter info.
    Otherwise, look for the hitter in the database. If not found, open the player page to obtain the hitter info.
    :param soup: BeautifulSoup object of the hitter in the daily lineups page
    :param team: team abbreviation of the hitter
    :param database_session: SQLAlchemy database session (default is None)
    """
    rotowire_id = get_id(soup)
    name = soup.find("a")["title"]
    position = soup.find("div", {"class": POSITION_CLASS_LABEL}).text
    hand = get_hand_bats(soup)

    return PlayerStruct(team, rotowire_id, position, hand, name, dfs_salary)


def get_pitcher(soup, team):
    """ Get a PlayerStruct representing a pitcher
    If a database session is not provided, open the player page to obtain the pitcher info.
    Otherwise, look for the pitcher in the database. If not found, open the player page to obtain the pitcher info.
    :param soup: BeautifulSoup object of the pitcher in the daily lineups page
    :param team: team abbreviation of the pitcher
    :param database_session: SQLAlchemy database session (default is None)
    """
    rotowire_id = get_id(soup)
    hand = get_hand_throws(soup)
    name = soup.find("a").text

    return PlayerStruct(team, rotowire_id, "P", hand, name)


def get_hand_throws(soup):
    """
    :param soup: BeautifulSoup node of the player
    :return: Hand of the player
    """
    return soup.find("span", {"class": "lineup__throws"}).text


def get_hand_bats(soup):
    """
    :param soup: BeautifulSoup node of the player
    :return: Hand of the player
    """
    return soup.find("span", {"class": "lineup__bats"}).text


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


def get_wind_speed(weather_node):
    """ Extract the wind speed from the Rotowire game soup
    :param soup: Rotowire soup for the individual game
    :return: an integer representation of the wind speed (negative for "In", positive for "Out", zero otherwise)
    """
    wind_text = weather_node.text
    wind_words = wind_text.strip().split()
    if wind_words[-1] == "Out":
        return int(wind_words[-3])
    elif wind_words[-1] == "In":
        return -1*int(wind_words[-3])

    return 0


def get_temperature(weather_node):
    """ Extract the temperature from the Rotowire game soup
    :param weather_node: Rotowire soup for the individual game
    :return: an integer representation of the temperature (in degrees Fahrenheit)
    """
    return weather_node.text.split()[2]


class UmpDataNotFound(Exception):

    def __init__(self):
        super(UmpDataNotFound, self).__init__("The ump data was not found in the soup")


def get_ump_name(soup):
    """ Extract the strikeouts per 9 innings for the ump for a given game
    :param soup: Rotowire soup for the individual game
    :return: float representation of the strikeouts per game
    """
    return soup.find("div", {"class": "lineup__umpire"}).find("a").text


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
            print("Game between %s and %s is not valid." % (matchup.away_team, matchup.home_team))
            continue

        matchups.append(matchup)

    return matchups
