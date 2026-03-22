
from dataclasses import dataclass

import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


@dataclass
class ParkFactor:
    id: int
    venue_name: str
    factor: int


class InvalidHeaderValueCount(Exception):
    """Exception raised when the number of header fields does not match the number of value fields in a table."""
    def __init__(self, header_count: int, value_count: int, table_name: str):
        self.header_count = header_count
        self.value_count = value_count
        self.table_name = table_name
        super().__init__(self.__str__())

    def __str__(self):
        return f"The number of header fields {self.header_count} does not equal the number of value fields {self.value_count} in the table {self.table_name}"


def str_to_num(strin: str) -> float | int | str:
    try:
        return int(strin)
    except ValueError:
        try:
            return int(strin.replace(",", ""))
        except ValueError:
            try:
                return float(strin)
            except ValueError:
                return strin


def get_park_factors(year: int, year_window: int = 1, browser: selenium.webdriver.Firefox = None) -> {str: ParkFactor}:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year={}&batSide=&stat=index_wOBA&condition=All&rolling={}&parks=mlb", year, year_window)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "parkFactors"
    factors_table = browser.find_element(By.ID, table_name)
    header = factors_table.find_element(By.TAG_NAME, "thead")
    header_names = [x.text for x in header.find_elements(By.TAG_NAME, "th")]

    table_body = factors_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_dict = dict()
    for row in table_rows:
        values = [x.text for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        output_dict[table_dict["Team"]] = ParkFactor(id=int(row.get_attribute("data-id")), venue_name=table_dict["Venue"], factor=int(table_dict["Park Factor"]))

    return output_dict


def get_exit_velocity(year: int, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/statcast?type=batter&year={}&position=&team=&min=1&sort=barrels_per_pa&sortDir=desc", year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "evLeaderboard"
    factors_table = browser.find_element(By.ID, table_name)
    header = factors_table.find_element(By.TAG_NAME, "thead")
    sub_header = header.find_element(By.CLASS_NAME, "tr-component-row")
    header_names = [x.text for x in sub_header.find_elements(By.TAG_NAME, "th")]

    # Add the prefix from the line above in the table
    prefix_headers = header.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
    current_col = 0
    for prefix_header in prefix_headers:
        colspan = int(prefix_header.get_attribute("colspan"))
        # There is a bug in Statcast where they don't define the column spans for the final columns correctly, so clamp it
        if current_col + colspan > len(header_names) - 1:
            colspan = len(header_names) - current_col
        if prefix_header.get_attribute("class") == "th-title-header":
            prefix = prefix_header.text
            if len(prefix) > 0:
                for i in range(current_col, current_col + colspan):
                    header_names[i] = prefix + " " + header_names[i]

        current_col += colspan

    table_body = factors_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_list = list()
    for row in table_rows:
        values = [str_to_num(x.text) for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        player_names = table_dict["Player"].split(",")
        table_dict["Player"] = (player_names[1] + " " + player_names[0]).strip()
        table_dict["Id"] = row.get_attribute("data-id")
        table_dict.pop("Team")
        output_list.append(table_dict)

    return pd.DataFrame(output_list)


def get_baserunning_run_value(year: int, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/baserunning-run-value?game_type=Regular&season_start={}&season_end={}&sortColumn=runner_runs_tot&sortDirection=desc&split=no&n=1&team=&type=Run&with_team_only=1", year, year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "baserunning_run_value_table"
    factors_table = browser.find_element(By.ID, table_name)
    header = factors_table.find_element(By.TAG_NAME, "thead")
    sub_header = header.find_element(By.CLASS_NAME, "tr-component-row")
    header_names = [x.text.replace("\n", "").strip() for x in sub_header.find_elements(By.TAG_NAME, "th")]

    # Add the prefix from the line above in the table
    prefix_headers = header.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
    current_col = 0
    for prefix_header in prefix_headers:
        colspan = int(prefix_header.get_attribute("colspan"))
        # There is a bug in Statcast where they don't define the column spans for the final columns correctly, so clamp it
        if current_col + colspan > len(header_names) - 1:
            colspan = len(header_names) - current_col
        if prefix_header.get_attribute("class") == "th-title-header":
            prefix = prefix_header.text
            if len(prefix) > 0:
                for i in range(current_col, current_col + colspan):
                    header_names[i] = prefix + " " + header_names[i]

        current_col += colspan

    table_body = factors_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_list = list()
    for row in table_rows:
        values = [str_to_num(x.text) for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        player_names = table_dict["Player"].split(",")
        table_dict["Player"] = (player_names[1] + " " + player_names[0]).strip()
        table_dict["Id"] = row.get_attribute("data-id").split("_")[0]
        table_dict.pop("Team")
        table_dict.pop("")
        output_list.append(table_dict)

    return pd.DataFrame(output_list)


def get_hitter_run_value(year: int, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/swing-take?year={}&team=&leverage=Neutral&group=Batter&type=All&sub_type=null&min=1", year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "runs"
    factors_table = browser.find_element(By.ID, table_name)
    header = factors_table.find_element(By.TAG_NAME, "thead")
    sub_header = header.find_element(By.CLASS_NAME, "tr-component-row")
    header_names = [x.text.replace("\n", "").strip() for x in sub_header.find_elements(By.TAG_NAME, "th")]

    # Add the prefix from the line above in the table
    prefix_headers = header.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
    current_col = 0
    for prefix_header in prefix_headers:
        colspan = int(prefix_header.get_attribute("colspan"))
        # There is a bug in Statcast where they don't define the column spans for the final columns correctly, so clamp it
        if current_col + colspan > len(header_names) - 1:
            colspan = len(header_names) - current_col
        if prefix_header.get_attribute("class") == "th-title-header":
            prefix = prefix_header.text
            if len(prefix) > 0:
                for i in range(current_col, current_col + colspan):
                    header_names[i] = prefix + " " + header_names[i]

        current_col += colspan

    table_body = factors_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_list = list()
    for row in table_rows:
        values = [str_to_num(x.text) for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        player_names = table_dict["Player"].split(",")
        table_dict["Player"] = (player_names[1] + " " + player_names[0]).strip()
        cells = row.find_elements(By.TAG_NAME, "td")
        for cell in cells:
            try:
                portait_element = cell.find_element(By.CLASS_NAME, "player-mug")
                table_dict["Id"] = portait_element.get_attribute("src").split("/")[-1].split(".")[0]
            except NoSuchElementException:
                pass
        table_dict.pop("Team")
        output_list.append(table_dict)

    return pd.DataFrame(output_list)


def get_pitcher_run_value(year: int, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/swing-take?year={}&team=&leverage=Neutral&group=Pitcher&type=All&sub_type=null&min=1", year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "runs"
    factors_table = browser.find_element(By.ID, table_name)
    header = factors_table.find_element(By.TAG_NAME, "thead")
    sub_header = header.find_element(By.CLASS_NAME, "tr-component-row")
    header_names = [x.text.replace("\n", "").strip() for x in sub_header.find_elements(By.TAG_NAME, "th")]

    # Add the prefix from the line above in the table
    prefix_headers = header.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
    current_col = 0
    for prefix_header in prefix_headers:
        colspan = int(prefix_header.get_attribute("colspan"))
        # There is a bug in Statcast where they don't define the column spans for the final columns correctly, so clamp it
        if current_col + colspan > len(header_names) - 1:
            colspan = len(header_names) - current_col
        if prefix_header.get_attribute("class") == "th-title-header":
            prefix = prefix_header.text
            if len(prefix) > 0:
                for i in range(current_col, current_col + colspan):
                    header_names[i] = prefix + " " + header_names[i]

        current_col += colspan

    table_body = factors_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_list = list()
    for row in table_rows:
        values = [str_to_num(x.text) for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        player_names = table_dict["Player"].split(",")
        table_dict["Player"] = (player_names[1] + " " + player_names[0]).strip()
        cells = row.find_elements(By.TAG_NAME, "td")
        for cell in cells:
            try:
                portait_element = cell.find_element(By.CLASS_NAME, "player-mug")
                table_dict["Id"] = portait_element.get_attribute("src").split("/")[-1].split(".")[0]
            except NoSuchElementException:
                pass
        table_dict.pop("Team")
        output_list.append(table_dict)

    return pd.DataFrame(output_list)


def get_hitter_vs_pitch_arsenal_stats(year: int, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type=batter&pitchType=&year={}&team=&min=1&minPitches=1&sort=4&sortDir=desc", year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "arsenalStats"
    arsenal_table = browser.find_element(By.ID, table_name)
    header = arsenal_table.find_element(By.TAG_NAME, "thead")
    sub_header = header.find_element(By.CLASS_NAME, "tr-component-row")
    header_names = [x.text.replace("\n", "").strip() for x in sub_header.find_elements(By.TAG_NAME, "th")]

    # Add the prefix from the line above in the table
    prefix_headers = header.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
    current_col = 0
    for prefix_header in prefix_headers:
        colspan = int(prefix_header.get_attribute("colspan"))
        # There is a bug in Statcast where they don't define the column spans for the final columns correctly, so clamp it
        if current_col + colspan > len(header_names) - 1:
            colspan = len(header_names) - current_col
        if prefix_header.get_attribute("class") == "th-title-header":
            prefix = prefix_header.text
            if len(prefix) > 0:
                for i in range(current_col, current_col + colspan):
                    header_names[i] = prefix + " " + header_names[i]

        current_col += colspan

    table_body = arsenal_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_list = list()
    for row in table_rows:
        values = [str_to_num(x.text) for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        player_names = table_dict["Player"].split(",")
        table_dict["Player"] = (player_names[1] + " " + player_names[0]).strip()
        cells = row.find_elements(By.TAG_NAME, "td")
        for cell in cells:
            try:
                portait_element = cell.find_element(By.CLASS_NAME, "player-mug")
                table_dict["Id"] = portait_element.get_attribute("src").split("/")[-1].split(".")[0]
            except NoSuchElementException:
                pass
        table_dict.pop("Team")
        output_list.append(table_dict)

    return pd.DataFrame(output_list)


def get_pitcher_arsenal_stats(year: int, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type=pitcher&pitchType=&year={}&team=&min=1&minPitches=1&sort=4&sortDir=desc", year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "arsenalStats"
    arsenal_table = browser.find_element(By.ID, table_name)
    header = arsenal_table.find_element(By.TAG_NAME, "thead")
    sub_header = header.find_element(By.CLASS_NAME, "tr-component-row")
    header_names = [x.text.replace("\n", "").strip() for x in sub_header.find_elements(By.TAG_NAME, "th")]

    # Add the prefix from the line above in the table
    prefix_headers = header.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "th")
    current_col = 0
    for prefix_header in prefix_headers:
        colspan = int(prefix_header.get_attribute("colspan"))
        # There is a bug in Statcast where they don't define the column spans for the final columns correctly, so clamp it
        if current_col + colspan > len(header_names) - 1:
            colspan = len(header_names) - current_col
        if prefix_header.get_attribute("class") == "th-title-header":
            prefix = prefix_header.text
            if len(prefix) > 0:
                for i in range(current_col, current_col + colspan):
                    header_names[i] = prefix + " " + header_names[i]

        current_col += colspan

    table_body = arsenal_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_list = list()
    for row in table_rows:
        values = [str_to_num(x.text) for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        player_names = table_dict["Player"].split(",")
        table_dict["Player"] = (player_names[1] + " " + player_names[0]).strip()
        cells = row.find_elements(By.TAG_NAME, "td")
        for cell in cells:
            try:
                portait_element = cell.find_element(By.CLASS_NAME, "player-mug")
                table_dict["Id"] = portait_element.get_attribute("src").split("/")[-1].split(".")[0]
            except NoSuchElementException:
                pass
        table_dict.pop("Team")
        output_list.append(table_dict)

    return pd.DataFrame(output_list)