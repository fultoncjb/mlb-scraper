
from beautiful_soup_helper import *

import selenium.webdriver.remote.webelement
import re

BASE_URL = "https://www.fangraphs.com"


class PlayerNameNotFound(Exception):
    def __init__(self, name_str):
        super(PlayerNameNotFound, self).__init__("Player '%s' not found in the Baseball Reference page" % name_str)


def get_hitter_id(full_name: str, team: str, year: int, browser: selenium.webdriver.Firefox = None) -> str:
    url = BASE_URL + "/teams/" + team + "/stats?season=" + str(year)

    soup = get_soup_from_url(url)
    hitter_table = soup.find("div", {"class": "team-stats-table"})
    hitter_rows = hitter_table.findAll("tr")
    for row in hitter_rows:
        regex_match = re.match("([a-zA-Z.']* [a-zA-Z.']*)", row.text)
        if regex_match is not None and regex_match.group(1) == full_name:
            hitter_link = row.find("a").get("href")
            return full_name.lower().replace(" ", "-") + "/" + re.search("playerid=([0-9]*)", hitter_link).group(1)

    # TODO add position portion of link to the output of this function
    # TODO but we need to separate the output since they are separated in the URL

    raise PlayerNameNotFound(full_name)


def get_hitter_stats_vs_pitch(fan_graphs_id:str, pitch_type: str):
    url = BASE_URL + "/players/" + fan_graphs_id + "/pitch-type-splits"


