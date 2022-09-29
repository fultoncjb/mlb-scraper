"""
draft_kings.py
Module used for scraping data from draftkings.com
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from urllib.request import urlretrieve
import csv

ROTOWIRE_DAILY_LINEUPS_URL = "http://www.rotowire.com/baseball/daily_lineups.htm"
ROTOWIRE_LINK_TEXT = "See daily player values on DraftKings"
CONTEST_SALARY = 50000


class NameNotFound(Exception):
    def __init__(self, name):
        super(NameNotFound, self).__init__("Name '%s' not found in the Draftkings page" %
                                                      name)


def save_daily_csv():
    browser = webdriver.Chrome()
    browser.get(ROTOWIRE_DAILY_LINEUPS_URL)
    draftkings_button = browser.find_element_by_link_text(ROTOWIRE_LINK_TEXT)
    draftkings_button.click()
    browser.switch_to.window(browser.window_handles[len(browser.window_handles)-1])
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'fancybox-outer')))
    print("Page loaded")
    browser.find_element_by_id("fancybox-close").click()
    #wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "tabs")]/ul/li[text() = "All"]')))
    #browser.find_element_by_xpath('//div[contains(@class, "tabs")]/ul/li[text() = "All"]').click()

    # download the file
    csv_url = urljoin(browser.current_url, browser.find_element_by_css_selector("a.export-to-csv").get_attribute("href"))
    urlretrieve(csv_url, "players.csv")


def get_csv_dict(filename=None):
    """ Create a dictionary of dictionaries indexed by a concatentation of name and Draftkings team abbreviation
    """
    if filename is None:
        filename = "players.csv"

    try:
        csv_dict = dict()
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_dict[(row["Name"] + row["teamAbbrev"]).lower()] = row
    except:
        csv_dict = None

    return csv_dict


def get_hitter_points(stat_dict: dict) -> float:
    points = float()
    points += 5 * float(stat_dict["2B"])
    points += 8 * float(stat_dict["3B"])
    points += 10 * float(stat_dict["HR"])
    points += 2 * float(stat_dict["RBI"])
    points += 2 * float(stat_dict["R"])
    points += 2 * float(stat_dict["BB"])
    points += 2 * float(stat_dict["HBP"])
    points += 5 * float(stat_dict["SB"])
    singles = float(stat_dict["H"]) - float(stat_dict["2B"]) - float(stat_dict["3B"]) - float(stat_dict["HR"])
    points += 3 * singles

    return points


def get_pitcher_points(stat_dict: dict) -> float:
    points = 0.0
    string_ip = str(stat_dict["IP"])
    innings_pitched_float = 0.333 * float(string_ip.split(".")[1]) + float(string_ip.split(".")[0])
    points += 2.25 * innings_pitched_float
    points += 2 * float(stat_dict["SO"])
    points += 4 * float(stat_dict["W"])
    points -= 2 * float(stat_dict["ER"])
    points -= 0.6 * float(stat_dict["H"])
    points -= 0.6 * float(stat_dict["BB"])
    points -= 0.6 * float(stat_dict["HBP"])
    # TODO may not be great assumptions in here
    # Complete game
    if float(stat_dict["CG"]) > 0.0:
        points += 2.5
        # Complete game shutout
        if float(stat_dict["R"]) < 1:
            points += 2.5
        # No hitter
        if float(stat_dict["H"]) < 1:
            points += 5

    return points