
from beautiful_soup_helper import *
from datetime import timedelta

BASE_URL = 'http://gd2.mlb.com/components/game/mlb/'


def int_to_two_digits(int_value):
    return "%02d" % (int_value,)


def get_game_ids(soup):
    """
    Get a list of game IDs from the input soup
    :param soup: BeautifulSoup object
    :return: list of game ID strings
    """
    game_ids = soup.select("a[href*=gid]")
    return [game_id.text.strip() for game_id in game_ids]


def get_previous_hitter_pitch_stats(player_id, team_abbrev, game_date):
    """
    Search backward from the given game date to find the hitter pitch tendencies by out
    :param player_id: Gameday player ID of hitter of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_date: game date
    :return: dictionary of the season hitter tendencies represented by outs recorded
    """
    current_time_delta = timedelta(days=1)
    while current_time_delta.days < 25:
        current_game_date = game_date - current_time_delta
        hitter_stats = get_season_hitter_pitch_stats(player_id, team_abbrev, current_game_date)
        if hitter_stats is None:
            current_time_delta += timedelta(days=1)
        else:
            return hitter_stats

    return None


def get_previous_pitcher_pitch_stats(player_id, team_abbrev, game_date):
    """
    Search backward from the given game date to find the pitcher pitch tendencies by out
    :param player_id: Gameday player ID of pitcher of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_date: game date
    :return: dictionary of the season pitcher tendencies represented by outs recorded
    """
    current_time_delta = timedelta(days=1)
    while current_time_delta.days < 25:
        current_game_date = game_date - current_time_delta
        pitcher_stats = get_season_pitcher_pitch_stats(player_id, team_abbrev, current_game_date)
        if pitcher_stats is None:
            current_time_delta += timedelta(days=1)
        else:
            return pitcher_stats

    return None


def get_season_hitter_pitch_stats(player_id, team_abbrev, game_date):
    """
    Get a dictionary of the season hitter tendencies represented by outs recorded
    :param player_id: Gameday player ID of hitter of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_date: game date
    :return: dictionary of the season hitter tendencies represented by outs recorded
    """

    try:
        url = BASE_URL + 'year_' + str(game_date.year) + '/' + 'month_' + int_to_two_digits(game_date.month) + '/' + 'day_' + \
              int_to_two_digits(game_date.day)
        # Get all the game IDs from the soup and find the matching team
        hitter_soup = get_soup_from_url(url)
        game_ids = get_game_ids(hitter_soup)
        # Find the relevant team in list of URLS
        matching_game_id = [game_id for game_id in game_ids if team_abbrev in game_id]

        # Get the batters URL
        season_dict = dict()
        batters_url = url + '/' + matching_game_id[0] + 'premium/batters/' + player_id + '/'
        # Changeups
        soup = get_soup_from_url(batters_url + 'pch.xml')
        season_dict['ch'] = soup.find('std').find('sit').attrs
        # Curveball
        soup = get_soup_from_url(batters_url + 'pcu.xml')
        season_dict['cu'] = soup.find('std').find('sit').attrs
        #
        soup = get_soup_from_url(batters_url + 'pfa.xml')
        season_dict['fa'] = soup.find('std').find('sit').attrs
        # Cutter
        soup = get_soup_from_url(batters_url + 'pfc.xml')
        season_dict['fc'] = soup.find('std').find('sit').attrs
        # Four-seam fastball
        soup = get_soup_from_url(batters_url + 'pff.xml')
        season_dict['ff'] = soup.find('std').find('sit').attrs
        #
        soup = get_soup_from_url(batters_url + 'pfs.xml')
        season_dict['fs'] = soup.find('std').find('sit').attrs
        # Two-seam fastball?
        soup = get_soup_from_url(batters_url + 'pft.xml')
        season_dict['ft'] = soup.find('std').find('sit').attrs
        # Knuckleball
        soup = get_soup_from_url(batters_url + 'pkn.xml')
        season_dict['kn'] = soup.find('std').find('sit').attrs
        # Sinker
        soup = get_soup_from_url(batters_url + 'psi.xml')
        season_dict['si'] = soup.find('std').find('sit').attrs
        # Slider
        soup = get_soup_from_url(batters_url + 'psl.xml')
        season_dict['sl'] = soup.find('std').find('sit').attrs

        return season_dict
    except (AttributeError, KeyError):
        return None


def get_season_pitcher_pitch_stats(player_id, team_abbrev, game_date):
    """
    Get a dictionary of the season pitcher tendencies represented by outs recorded
    :param player_id: Gameday player ID of pitcher of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_date: game date
    :return: dictionary of the season pitcher tendencies represented by outs recorded
    """
    try:
        url = BASE_URL + 'year_' + str(game_date.year) + '/' + 'month_' + int_to_two_digits(game_date.month) + '/' + 'day_' + \
              int_to_two_digits(game_date.day)
        # Get all the game IDs from the soup and find the matching team
        hitter_soup = get_soup_from_url(url)
        game_ids = get_game_ids(hitter_soup)
        # Find the relevant team in list of URLS
        matching_game_id = [game_id for game_id in game_ids if team_abbrev in game_id]

        # Get the batters URL
        season_dict = dict()
        batters_url = url + '/' + matching_game_id[0] + 'premium/pitchers/' + player_id + '/'
        # Changeups
        soup = get_soup_from_url(batters_url + 'pch.xml')
        season_dict['ch'] = soup.find('std').find('sit').attrs
        # Curveball
        soup = get_soup_from_url(batters_url + 'pcu.xml')
        season_dict['cu'] = soup.find('std').find('sit').attrs
        #
        soup = get_soup_from_url(batters_url + 'pfa.xml')
        season_dict['fa'] = soup.find('std').find('sit').attrs
        # Cutter
        soup = get_soup_from_url(batters_url + 'pfc.xml')
        season_dict['fc'] = soup.find('std').find('sit').attrs
        # Four-seam fastball
        soup = get_soup_from_url(batters_url + 'pff.xml')
        season_dict['ff'] = soup.find('std').find('sit').attrs
        #
        soup = get_soup_from_url(batters_url + 'pfs.xml')
        season_dict['fs'] = soup.find('std').find('sit').attrs
        # Two-seam fastball?
        soup = get_soup_from_url(batters_url + 'pft.xml')
        season_dict['ft'] = soup.find('std').find('sit').attrs
        # Knuckleball
        soup = get_soup_from_url(batters_url + 'pkn.xml')
        season_dict['kn'] = soup.find('std').find('sit').attrs
        # Sinker
        soup = get_soup_from_url(batters_url + 'psi.xml')
        season_dict['si'] = soup.find('std').find('sit').attrs
        # Slider
        soup = get_soup_from_url(batters_url + 'psl.xml')
        season_dict['sl'] = soup.find('std').find('sit').attrs

        return season_dict
    except (KeyError, AttributeError):
        return None


def get_game_pitcher_tendencies(player_id, team_abbrev, game_date):
    """
    Get a dictionary of the pitcher pitch type tendencies during the given game date
    :param player_id: Gameday ID of the pitcher of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_date: game date
    :return: dictionary of pitch type abbreviations to tendency stats
    """
    url = BASE_URL + 'year_' + str(game_date.year) + '/' + 'month_' + int_to_two_digits(game_date.month) + '/' + 'day_' + \
          int_to_two_digits(game_date.day)
    # Get all the game IDs from the soup and find the matching team
    hitter_soup = get_soup_from_url(url)
    game_ids = get_game_ids(hitter_soup)
    # Find the relevant team in list of URLS
    matching_game_id = [game_id for game_id in game_ids if team_abbrev in game_id]

    # Get the batters URL
    season_dict = dict()
    batters_url = url + '/' + matching_game_id[0] + 'premium/pitchers/' + player_id + '/'
    #
    soup = get_soup_from_url(batters_url + 'pitchtendencies_game.xml')

    game_pitch_types = soup.find('std').find('types').findAll('type')
    for game_pitch_type in game_pitch_types:
        season_dict[game_pitch_type.attrs['id']] = game_pitch_type.attrs

    return season_dict

