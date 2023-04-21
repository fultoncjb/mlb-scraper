
from datetime import *
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

    url = "https://stathead.com/baseball/batter_vs_pitcher.cgi?request=1&year_min=" + str(min_year) + "&year_max=" + str(max_year) + "&batter=" + hitter_id
    browser.get(url)

    # TODO need to now extract the data
    # TODO return generalized object with the table data so we can pick out a specific pitcher in a helper method

    # TODO we can actually get this by plate appearance using Stathead.
    # TODO so we can save those events to the database and we can get the accurate pregame data from that

    main_table = browser.find_element(By.ID, "result_table")
    table_rows = main_table.find_elements(By.TAG_NAME, "tr")
    for row in table_rows:
        print(row)


def get_vs_pitcher_gamelogs(hitter_id: PlayerIdentifier, pitcher_id: str, credentials: (str, str),
                            browser: selenium.webdriver.Firefox = None) -> [dict]:
    if browser is None:
        browser = login_stathead(credentials)

    url = "https://stathead.com/baseball/batter_vs_pitcher.cgi?request=1&post=1&batter=" + hitter_id.get_id() + "&pitcher=" + pitcher_id
    browser.get(url)

    main_table = browser.find_element(By.ID, "all_ajax_result_table_1")
    table_rows = main_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

    output_rows = list()
    team = None
    pitcher_team = None
    current_date = None
    for row in table_rows:
        if len(row.get_attribute("class")) == 0:

            # Interpret what happened during the plate apperance
            play_element = row.find_element(By.XPATH, ".//td[@data-stat='play_desc']")
            row_dict = interpret_plate_appearance_result_string(play_element.text, hitter_id)
            row_dict["PlayDescription"] = play_element.text

            # Find the team ID
            team_element = row.find_element(By.XPATH, ".//td[@data-stat='team_id']")
            if team_element is not None and len(team_element.text) > 0:
                team = team_element.text
            if team is None:
                raise PlayerNameNotFound # TODO need a better exception to throw
            row_dict["HitterTeam"] = team

            # Find the opposing team ID
            pitcher_team_element = row.find_element(By.XPATH, ".//td[@data-stat='opp_ID']")
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
            date_element = row.find_element(By.XPATH, ".//td[@data-stat='date_game']")
            if date_element is not None and len(date_element.text) > 0:
                date_text = date_element.text
                current_date = datetime.combine(date.fromisoformat(date_text), datetime.min.time())
            if current_date is None and len(date_element.text) > 0:
                raise PlayerNameNotFound
            row_dict["Date"] = current_date

            row_dict["Sequence"] = int(row.find_element(By.TAG_NAME, "th").text)
            row_dict["HitterId"] = hitter_id.get_id()
            row_dict["PitcherId"] = pitcher_id
            output_rows.append(row_dict)

    return output_rows


def interpret_plate_appearance_result_string(input_str: str, hitter_id: PlayerIdentifier) -> dict:
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

    output_dict["RBI"] = get_num_rbis(input_str, hitter_id)

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


def get_num_rbis(play_description: str, hitter_id: PlayerIdentifier) -> int:
    num_rbis = len(re.findall("Scores", play_description))
    num_rbis -= len(re.findall("No RBI", play_description))
    # If the hitter hit a home run, then they get an RBI for knocking themselves in
    if re.search("Home Run", play_description) is not None:
        # Sometimes for some reason Stathead includes the hitter's name as scoring and sometimes not
        if re.search(hitter_id.get_last_name() + " Scores", play_description) is None:
            num_rbis += 1
    if num_rbis > 0:
        if re.search("on E([0-9])", play_description) is not None:
            #num_rbis -= 1
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

    url = "https://stathead.com/baseball/batter_vs_pitcher.cgi?request=1&post=1&batter=" + hitter_id
    browser.get(url)

    main_table = browser.find_element(By.ID, "result_table")
    table_rows = main_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
    for row in table_rows:
        try:
            pitcher_url = row.find_element(By.TAG_NAME, "th").get_attribute("data-append-csv")
            plate_apperances = int(row.find_element(By.XPATH, ".//td[@data-stat='PA']").text)
            rbis = int(row.find_element(By.XPATH, ".//td[@data-stat='RBI']").text)
            if pitcher_url is not None:
                pitcher_id = re.match(".*pitcher=([a-z'._]*.?[0-9]*)", pitcher_url)
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

    url = "https://stathead.com/baseball/player-batting-season-finder.cgi"

    if year is None:
        year = date.today().year

    browser.get(url)

    stat_filter_set = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pi_filter_sets")))

    dropdown_element = stat_filter_set.find_element(By.CLASS_NAME, " no chosen")
    bio_stat_dropdown = Select(dropdown_element.find_element(By.TAG_NAME, "select"))
    bio_stat_dropdown.select_by_visible_text("Name Starts/Ends With")





