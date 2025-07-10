
from datetime import *

import pandas as pd
import selenium.webdriver.remote.webelement
from selenium import webdriver
from selenium.webdriver import remote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
from baseball_reference import PlayerIdentifier, PlayerNameNotFound
from time import sleep


HITTER_RELEVANT_STAT_KEYS = ["G", "PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "SB", "CS", "BB", "SO", "TB",
                             "GIDP", "HBP", "SH", "SF", "IBB"]

def login_stathead(credentials: (str, str)) -> selenium.webdriver.Firefox:
    login_url = "https://stathead.com/users/login.cgi"

    # Login to Stathead to unlock all the data
    browser = webdriver.Firefox()
    browser.get(login_url)
    username_field = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.ID, "username")))
    username_field.send_keys(credentials[0])
    password_field = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.ID, "password")))
    password_field.send_keys(credentials[1])
    login_button = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.ID, "sh-login-button")))
    login_button.click()

    return browser


def get_vs_pitcher(hitter_id: str, min_year: int, max_year: int, credentials: (str, str)):

    browser = login_stathead(credentials)

    url = "https://stathead.com/baseball/batter_vs_pitcher.cgi?request=1&year_min=%i&year_max=%i&batter=%s" % (min_year, max_year, hitter_id)
    browser.get(url)

    # TODO need to now extract the data
    # TODO return generalized object with the table data so we can pick out a specific pitcher in a helper method

    # TODO we can actually get this by plate appearance using Stathead.
    # TODO so we can save those events to the database and we can get the accurate pregame data from that

    main_table = browser.find_element(By.ID, "result_table")
    table_rows = main_table.find_elements(By.TAG_NAME, "tr")
    for row in table_rows:
        print(row)


def get_vs_pitcher_gamelogs(hitter_stathead_id: str, hitter_last_name: str, pitcher_stathead_id: str,
                            credentials: (str, str), browser: selenium.webdriver.Firefox = None) -> [dict]:
    if browser is None:
        browser = login_stathead(credentials)

    url = "https://stathead.com/baseball/versus-finder.cgi?request=1&post=1&player_id1=%s&player_id2=%s" % (hitter_stathead_id, pitcher_stathead_id)
    browser.get(url)

    table_list = list()
    num_attempts = 0
    while num_attempts < 3:
        try:
            table_list.append(browser.find_element(By.ID, "div_stats_bvp_pa_rs"))
            break
        except selenium.common.exceptions.NoSuchElementException:
            break
        except selenium.common.exceptions.WebDriverException as e:
            sleep(5.0)
            browser.get(url)
            num_attempts = num_attempts + 1
            if num_attempts >= 3:
                raise e
            pass
    try:
        table_list.append(browser.find_element(By.ID, "div_stats_bvp_pa_po"))
    except selenium.common.exceptions.NoSuchElementException:
        pass

    output_rows = list()
    team = None
    pitcher_team = None
    current_date = None
    for idx, table in enumerate(table_list):
        # In order to enable the playoffs stats, we must click the button
        if idx == 1:
            main_table = browser.find_element(By.ID, "all_stathead_results_bvp_pa")
            switcher_element = main_table.find_element(By.XPATH, ".//div[@data-controls='#switcher_stathead_results_bvp_pa']")
            playoffs_button = WebDriverWait(switcher_element, 5).until(
                EC.element_to_be_clickable((By.XPATH, ".//a[@data-show='.assoc_stats_bvp_pa_po']")))
            playoffs_button.click()
        table_rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
        for row in table_rows:
            if len(row.get_attribute("class")) == 0:

                # Interpret what happened during the plate apperance
                play_element = row.find_element(By.XPATH, ".//td[@data-stat='play_desc']")
                row_dict = interpret_plate_appearance_result_string(play_element.text, hitter_last_name)
                row_dict["PlayDescription"] = play_element.text

                # Find the team ID
                team_element = row.find_element(By.XPATH, ".//td[@data-stat='event_b_team']")
                if team_element is not None and len(team_element.text) > 0:
                    team = team_element.text
                if team is None:
                    raise PlayerNameNotFound # TODO need a better exception to throw
                row_dict["HitterTeam"] = team

                # Find the opposing team ID
                pitcher_team_element = row.find_element(By.XPATH, ".//td[@data-stat='event_p_team']")
                if pitcher_team_element is not None and len(pitcher_team_element.text) > 0:
                    pitcher_team = pitcher_team_element.text
                if pitcher_team is None:
                    raise PlayerNameNotFound
                row_dict["PitcherTeam"] = pitcher_team

                # Find the score field
                score_element = row.find_element(By.XPATH, ".//td[@data-stat='team_rel_score']")
                row_dict["ScoreString"] = score_element.text

                # Find the inning field
                inning_element = row.find_element(By.XPATH, ".//td[@data-stat='inning']")
                row_dict["Inning"] = inning_element.text

                # Interpret the runners on base field
                rob_element = row.find_element(By.XPATH, ".//td[@data-stat='runners_on_bases']")
                is_runner_on_first = False
                if re.search("1", rob_element.text) is not None:
                    is_runner_on_first = True
                row_dict["RunnerOnFirst"] = is_runner_on_first
                is_runner_on_second = False
                if re.search("2", rob_element.text) is not None:
                    is_runner_on_second = True
                row_dict["RunnerOnSecond"] = is_runner_on_second
                is_runner_on_third = False
                if re.search("3", rob_element.text) is not None:
                    is_runner_on_third = True
                row_dict["RunnerOnThird"] = is_runner_on_third

                # Find the number of outs
                out_element = row.find_element(By.XPATH, ".//td[@data-stat='outs']")
                row_dict["Outs"] = int(out_element.text)

                # Interpret the count field (i.e. total pitches, balls, strikes
                count_element = row.find_element(By.XPATH, ".//td[@data-stat='pitches_pbp']")
                count_match = re.match("([0-9]*) \(([0-9]*)-([0-9]*)\)", count_element.text)
                # Some games early on do not have these fields populated
                if count_match is not None:
                    row_dict["Pitches"] = int(count_match.group(1))
                    row_dict["Balls"] = int(count_match.group(2))
                    row_dict["Strikes"] = int(count_match.group(3))

                # Interpret the date field
                date_element = row.find_element(By.XPATH, ".//td[@data-stat='date']")
                if date_element is not None and len(date_element.text) > 0:
                    date_text = date_element.text
                    date_text = date_text.split(" ")[0] # Remove double-header designations
                    current_date = datetime.combine(date.fromisoformat(date_text), datetime.min.time())
                if current_date is None and len(date_element.text) > 0:
                    raise PlayerNameNotFound
                row_dict["Date"] = current_date

                row_dict["Sequence"] = int(row.find_element(By.TAG_NAME, "th").text)
                row_dict["HitterId"] = hitter_stathead_id
                row_dict["PitcherId"] = pitcher_stathead_id
                output_rows.append(row_dict)

    return output_rows


def interpret_plate_appearance_result_string(input_str: str, hitter_last_name: str) -> dict:
    output_dict = dict()

    # Set the defaults
    output_dict["AB"] = 0.0
    output_dict["H"] = 0.0
    output_dict["2B"] = 0.0
    output_dict["3B"] = 0.0
    output_dict["HR"] = 0.0
    output_dict["RBI"] = 0.0
    output_dict["BB"] = 0.0
    output_dict["SO"] = 0.0
    output_dict["SH"] = 0.0
    output_dict["SF"] = 0.0
    output_dict["IBB"] = 0.0
    output_dict["HBP"] = 0.0
    output_dict["GDP"] = 0.0
    output_dict["PA"] = 1.0

    is_at_bat = True
    if is_hit_string(input_str):
        output_dict["H"] = 1

    if is_double(input_str):
        output_dict["2B"] = 1
    elif is_triple(input_str):
        output_dict["3B"] = 1
    elif re.search("Home Run", input_str) is not None:
        output_dict["HR"] = 1
    elif re.search("Strikeout", input_str) is not None:
        output_dict["SO"] = 1
    elif re.search("Intentional Walk", input_str) is not None:
        output_dict["BB"] = 1
        output_dict["IBB"] = 1
        is_at_bat = False
    elif re.search("Walk", input_str) is not None:
        output_dict["BB"] = 1
        is_at_bat = False
    elif re.search("Hit By Pitch", input_str) is not None:
        output_dict["HBP"] = 1
        is_at_bat = False
    elif re.search("Ground Ball Double Play", input_str) is not None:
        output_dict["GDP"] = 1
    elif re.search("Sacrifice Fly", input_str) is not None:
        output_dict["SF"] = 1
        is_at_bat = False
    elif re.search("Bunt Groundout", input_str) is not None and re.search("Sacrifice", input_str) is not None:
        output_dict["SH"] = 1
        is_at_bat = False

    output_dict["RBI"] = get_num_rbis(input_str, hitter_last_name)

    if is_at_bat:
        output_dict["AB"] = 1
    else:
        output_dict["AB"] = 0

    return output_dict


def is_hit_string(play_description: str) -> bool:
    if re.search("Single", play_description) is not None or \
       is_double(play_description) or \
       is_triple(play_description) or \
       re.search("Home Run", play_description) is not None:
        return True


def is_double(play_description: str) -> bool:
    return re.search("Double", play_description) is not None and re.search("Double Play", play_description) is None


def is_triple(play_description: str) -> bool:
    return re.search("Triple", play_description) is not None and re.search("Triple Play", play_description) is None


def get_num_rbis(play_description: str, hitter_last_name: str) -> int:
    num_rbis = len(re.findall("Scores", play_description))
    num_rbis -= len(re.findall("No RBI", play_description))
    # If the hitter hit a home run, then they get an RBI for knocking themselves in
    if re.search("Home Run", play_description) is not None:
        # Sometimes for some reason Stathead includes the hitter's name as scoring and sometimes not
        if re.search(hitter_last_name + " Scores", play_description) is None:
            num_rbis += 1
    if num_rbis > 0:
        if re.search("on E([0-9])", play_description) is not None:
            num_rbis -= 1
            print("ERROR PLAY! Rbis " + str(num_rbis))
            print(play_description)
        if re.search("Ground Ball Double Play", play_description) is not None:
            num_rbis = 0

    return num_rbis


def get_career_hitter_vs_ids(hitter_id: str, credentials: (str, str),
                             browser: selenium.webdriver.Firefox = None) -> (selenium.webdriver.Firefox, [str, int]):
    pitcher_ids = list()

    if browser is None:
        browser = login_stathead(credentials)

    url = "https://stathead.com/baseball/versus-finder.cgi?request=1&player_id1=" + hitter_id
    browser.get(url)

    main_table = browser.find_element(By.ID, "stats_bvp_sum_p_rs")
    table_rows = main_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
    for row in table_rows:
        try:
            pitcher_url = row.find_element(By.TAG_NAME, "td").get_attribute("data-append-csv")
            plate_apperances = int(row.find_element(By.XPATH, ".//td[@data-stat='b_pa']").text)
            rbis = int(row.find_element(By.XPATH, ".//td[@data-stat='b_rbi']").text)
            if pitcher_url is not None:
                pitcher_id = re.match(".*player_id2=([a-z0-9'._-]*)", pitcher_url)
                pitcher_ids.append((pitcher_id.group(1), plate_apperances, rbis))
        except selenium.common.exceptions.NoSuchElementException:
            continue

    return browser, pitcher_ids


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


def get_hitter_id(full_name, team, browser: selenium.webdriver.Firefox, year=None):
    # TODO this method is not currently supported

    url = "https://stathead.com/baseball/player-batting-season-finder.cgi"

    if year is None:
        year = date.today().year

    browser.get(url)

    stat_filter_set = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pi_filter_sets")))

    dropdown_element = stat_filter_set.find_element(By.CLASS_NAME, " no chosen")
    bio_stat_dropdown = Select(dropdown_element.find_element(By.TAG_NAME, "select"))
    bio_stat_dropdown.select_by_visible_text("Name Starts/Ends With")


def get_season_hitter_identifiers_and_pa(year_start: int,  credentials: (str, str),
                                  browser: selenium.webdriver.Firefox = None, year_end: int = None):
    # TODO this does not take into account all the players since there are multiple pages
    if year_end is None:
        year_end = year_start

    url = "https://stathead.com/baseball/player-batting-season-finder.cgi?request=1&year_min=%i&year_max=%i" % (year_start, year_end)

    if browser is None:
        browser = login_stathead(credentials)
    browser.get(url)

    results = browser.find_element(By.ID, "all_stathead_results")
    stats_table = results.find_element(By.ID, "div_stats").find_element(By.TAG_NAME, "tbody")
    player_rows = stats_table.find_elements(By.TAG_NAME, "tr")

    season_hitter_ids = list()
    for player_row in player_rows:
        if player_row.get_attribute("class") != "thead":
            player_name_entry = player_row.find_element(By.XPATH, ".//td[@data-stat='name_display']")
            player_link = player_name_entry.find_element(By.TAG_NAME, "a")
            link_text = player_link.get_attribute("href")
            hitter_id = re.match(".*/([a-z'._]*.?[0-9]*).shtml", link_text).group(1)
            hitter_name = player_link.text
            # For the team abbreviation, only the team they started the season on is used
            team_abbrev = player_row.find_element(By.XPATH, ".//td[@data-stat='teams_played_for']").text.split(",")[0]
            plate_apperances = int(player_row.find_element(By.XPATH, ".//td[@data-stat='b_pa']").text)

            season_hitter_ids.append((PlayerIdentifier(hitter_name, hitter_id, team_abbrev), plate_apperances))

    return season_hitter_ids


def get_season_pitcher_identifiers_and_bf(year_start: int,  credentials: (str, str),
                                  browser: selenium.webdriver.Firefox = None, year_end: int = None):
    # TODO this does not take into account all the players since there are multiple pages
    if year_end is None:
        year_end = year_start

    url = "https://stathead.com/baseball/player-pitching-season-finder.cgi?request=1&year_min=%i&year_max=%i" % (year_start, year_end)

    if browser is None:
        browser = login_stathead(credentials)
    browser.get(url)

    results = browser.find_element(By.ID, "all_stathead_results")
    stats_table = results.find_element(By.ID, "div_stats").find_element(By.TAG_NAME, "tbody")
    player_rows = stats_table.find_elements(By.TAG_NAME, "tr")

    ids = list()
    for player_row in player_rows:
        if player_row.get_attribute("class") != "thead":
            player_name_entry = player_row.find_element(By.XPATH, ".//td[@data-stat='name_display']")
            player_link = player_name_entry.find_element(By.TAG_NAME, "a")
            link_text = player_link.get_attribute("href")
            player_id = re.match(".*/([a-z'._]*.?[0-9]*).shtml", link_text).group(1)
            name = player_link.text
            # For the team abbreviation, only the team they started the season on is used
            team_abbrev = player_row.find_element(By.XPATH, ".//td[@data-stat='teams_played_for']").text.split(",")[0]
            batters_faced = int(player_row.find_element(By.XPATH, ".//td[@data-stat='p_bfp']").text)

            ids.append((PlayerIdentifier(name, player_id, team_abbrev), batters_faced))

    return ids


def get_career_hitting_stats(baseball_reference_id: str, player_name: str, is_postseason: bool, credentials: (str, str) = None,
                             browser: selenium.webdriver.Firefox = None) -> dict:

    split_name = player_name.split(" ")
    first_name = split_name[0]
    first_max_idx = min(len(first_name), 4)
    last_name = split_name[1]
    last_max_idx = min(len(last_name), 4)

    url = "https://stathead.com/baseball/player-batting-season-finder.cgi?request=1&match=player_season_combined" \
          "&first_name_starts=%s&last_name_starts=%s" % (first_name[0:first_max_idx], last_name[0:last_max_idx])

    if is_postseason:
        url += "&comp_type=post"

    if browser is None:
        browser = login_stathead(credentials)
    browser.get(url)

    try:
        results = browser.find_element(By.ID, "all_stathead_results")
        stats_object = results.find_element(By.ID, "div_stats")
        stats_table = stats_object.find_element(By.TAG_NAME, "tbody")
        player = stats_table.find_element(By.CSS_SELECTOR,
                                          "td[data-append-csv='%s']" % baseball_reference_id.replace("'", "\\'"))
        player_row = player.find_element(By.XPATH, "./..")
        stat_tags = stats_object.find_element(By.TAG_NAME, "thead")
        stat_key_list = list()
        for stat_key in stat_tags.find_elements(By.TAG_NAME, "th"):
            if stat_key.text != "Rk":
                stat_key_list.append(stat_key.text)
        stat_list = list()
        for stat in player_row.find_elements(By.TAG_NAME, "td"):
            stat_list.append(stat.text)

        output_dict = dict()
        for i in range(0, len(stat_key_list)):
            stat_key = stat_key_list[i]
            if stat_key in HITTER_RELEVANT_STAT_KEYS:
                try:
                    output_dict[stat_key_list[i]] = int(stat_list[i])
                except ValueError:
                    output_dict[stat_key_list[i]] = 0

        return output_dict
    except selenium.common.exceptions.NoSuchElementException:
        return {stat: 0 for stat in HITTER_RELEVANT_STAT_KEYS}


def get_season_hitting_game_logs(stathead_id: str, year: int, credentials: (str, str) = None, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    # TODO they split the season and postseason
    url = "https://stathead.com/baseball/player-batting-game-finder.cgi?request=1&player_id=%s&timeframe=seasons&year_min=%i&year_max=%i" % (stathead_id, year, year)

    if browser is None:
        browser = login_stathead(credentials)
    browser.get(url)

    table = browser.find_element(By.ID, "stats")
    table_header = table.find_element(By.TAG_NAME, "thead")
    table_header_names = [element.text for element in table_header.find_elements(By.TAG_NAME, "th")]
    table_body = table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.TAG_NAME, "tr")

    dict_list = list()

    for row in table_rows:
        # The 'Rk' at-bat counter is a 'th' tag, but there shouldn't be any others
        header_fields = row.find_elements(By.TAG_NAME, "th")
        if len(header_fields) > 1:
            continue
        entries = header_fields + row.find_elements(By.TAG_NAME, "td")
        if len(entries) != len(table_header_names):
            continue
        stat_dict = dict()
        for i in range(0, len(entries)):
            table_header_name = table_header_names[i]
            if len(table_header_name) == 0:
                table_header_name = "IsHome"
            try:
                num = int(entries[i].text)
                stat_dict[table_header_name] = num
            except ValueError:
                try:
                    num = float(entries[i].text)
                    stat_dict[table_header_name] = num
                except ValueError:
                    if table_header_name == "IsHome":
                        if entries[i].text == "@":
                            val = False
                        else:
                            val = True
                    else:
                        if len(entries[i].text) == 0:
                            val = 0
                        else:
                            val = entries[i].text
                    stat_dict[table_header_name] = val
            if table_header_name == "Player":
                player_link = entries[i].find_element(By.TAG_NAME, "a").get_attribute("href")
                match = re.search(r'([^/]+)(?=\.shtml)', player_link)
                stat_dict["br_id"] = match.group()

        dict_list.append(stat_dict)

    return pd.DataFrame(dict_list)


def get_season_pitching_game_logs(stathead_id: str, year: int, credentials: (str, str) = None, browser: selenium.webdriver.Firefox = None) -> pd.DataFrame:
    # TODO they split the season and postseason
    url = "https://stathead.com/baseball/player-pitching-game-finder.cgi?request=1&player_id=%s&timeframe=seasons&year_min=%i&year_max=%i" % (stathead_id, year, year)

    if browser is None:
        browser = login_stathead(credentials)
    browser.get(url)

    table = browser.find_element(By.ID, "stats")
    table_header = table.find_element(By.TAG_NAME, "thead")
    table_header_names = [element.text for element in table_header.find_elements(By.TAG_NAME, "th")]
    table_body = table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.TAG_NAME, "tr")

    dict_list = list()

    for row in table_rows:
        # The 'Rk' at-bat counter is a 'th' tag, but there shouldn't be any others
        header_fields = row.find_elements(By.TAG_NAME, "th")
        if len(header_fields) > 1:
            continue
        entries = header_fields + row.find_elements(By.TAG_NAME, "td")
        if len(entries) != len(table_header_names):
            continue
        stat_dict = dict()
        for i in range(0, len(entries)):
            table_header_name = table_header_names[i]
            if len(table_header_name) == 0:
                table_header_name = "IsHome"
            try:
                num = int(entries[i].text)
                stat_dict[table_header_name] = num
            except ValueError:
                try:
                    num = float(entries[i].text)
                    stat_dict[table_header_name] = num
                except ValueError:
                    if table_header_name == "IsHome":
                        if entries[i].text == "@":
                            val = False
                        else:
                            val = True
                    else:
                        if len(entries[i].text) == 0:
                            val = 0
                        else:
                            val = entries[i].text
                    stat_dict[table_header_name] = val
            if table_header_name == "Player":
                player_link = entries[i].find_element(By.TAG_NAME, "a").get_attribute("href")
                match = re.search(r'([^/]+)(?=\.shtml)', player_link)
                stat_dict["br_id"] = match.group()

        dict_list.append(stat_dict)

    return pd.DataFrame(dict_list)










