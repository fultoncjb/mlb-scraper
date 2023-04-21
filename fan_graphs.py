
from beautiful_soup_helper import *

import selenium.webdriver.remote.webelement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

BASE_URL = "https://www.fangraphs.com"


class PlayerNameNotFound(Exception):
    def __init__(self, name_str):
        super(PlayerNameNotFound, self).__init__("Player '%s' not found in the Baseball Reference page" % name_str)


class SeasonNotFound(Exception):
    def __init__(self, year):
        super(SeasonNotFound, self).__init__("Season not found for year '%i' in table" % year)


"""
FA = fastball
SI = sinker
SL = slider
CH = changeup
CU = curveball
FC = cutter
FS = splitter
KN = knuckleball
CS = slow cruve/eephus
SB = screwball
"""
PITCH_TYPES = ["FA", "SI", "SL", "CH", "CU", "FC", "FS", "KN", "CS", "SB"]


def get_hitter_id(full_name: str, team: str, year: int) -> (str, str):
    """
    Get the unique identifying information for a particular hitter who played for a particular team in a particular season.
    Note: the unique identifying information for a player involves their name, a unique integer, and their position.
    Their position is required because for some reason it is required to formulate FanGraphs URLs.
    :param full_name: the first and last name of the player
    :type full_name: str
    :param team: the name of the team the player played for in a given season. note: these team names use modified snake case as opposed to typical abbrevations
    :type team: str
    :param year: year the player played on a particular team
    :type year: int
    :param browser: browser object used for interacting with the browser
    :type browser: selenium.webdriver.Firefox
    :return: tuple of the concatenation of the players name and unique integer and the player's position
    :rtype: (str, str)
    """
    url = BASE_URL + "/teams/" + team + "/stats?season=" + str(year)

    soup = get_soup_from_url(url)
    hitter_table = soup.find("div", {"class": "team-stats-table"})
    hitter_rows = hitter_table.findAll("tr")
    for row in hitter_rows:
        regex_match = re.match("([a-zA-Z.']* [a-zA-Z.']*)", row.text)
        if regex_match is not None and regex_match.group(1) == full_name:
            hitter_link = row.find("a").get("href")
            id_position_regex_match = re.search("playerid=([0-9]*)&position=([0-9A-Z]*)", hitter_link)
            if id_position_regex_match is not None:
                return full_name.lower().replace(" ", "-") + "/" + id_position_regex_match.group(1), id_position_regex_match.group(2)

    raise PlayerNameNotFound(full_name)


def get_hitter_stats_vs_pitch(fan_graphs_id_tuple: (str, str), year: int, pitch_type: str, browser: selenium.webdriver.Firefox = None) -> dict:
    url = BASE_URL + "/players/" + fan_graphs_id_tuple[0] + "/pitch-type-splits?position=" + fan_graphs_id_tuple[1] + "&data=pi&pitchtype=" + pitch_type

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    # Close promotional modal if it exists
    button_class_name = "CloseButton__ButtonElement-sc-79mh24-0 eXoQFD loneoak-CloseButton loneoak-close loneoak-ClosePosition--top-right"
    try:
        modal_button = WebDriverWait(browser, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, button_class_name)))
        modal_button.click()
    except selenium.common.exceptions.TimeoutException:
        print("Warning! FanGraph promotional modal not present")

    table = browser.find_element(By.ID, "standard")

    table_rows = table.find_elements(By.CLASS_NAME, "row-mlb-season")

    stat_dict = dict()
    for row in table_rows:
        is_correct_year = False
        for field in row.find_elements(By.TAG_NAME, "td"):
            field_name = field.get_attribute("data-stat")
            try:
                if field_name == "Season" and int(field.text) == year:
                    is_correct_year = True
                    break
            except ValueError:
                break

        if is_correct_year:
            for field in row.find_elements(By.TAG_NAME, "td"):
                field_name = field.get_attribute("data-stat")
                stat_dict[field_name] = field.text

            return stat_dict

    raise SeasonNotFound(year)




