
from beautiful_soup_helper import *
from datetime import timedelta
import time

BASE_URL = 'http://gd2.mlb.com/components/game/mlb/'


def int_to_two_digits(int_value):
    return "%02d" % (int_value,)


class GameInfo(object):
    def __init__(self, game_date, game_id):
        self.game_date = game_date
        self.game_id = game_id


def get_game_ids(game_date):
    """
    Get a list of game IDs from the input soup
    :param soup: BeautifulSoup object
    :return: list of game ID strings
    """
    url = BASE_URL + 'year_' + str(game_date.year) + '/' + 'month_' + int_to_two_digits(
        game_date.month) + '/' + 'day_' + \
          int_to_two_digits(game_date.day)
    # Get all the game IDs from the soup and find the matching team
    soup = get_soup_from_url(url)
    game_ids = soup.select("a[href*=gid]")
    return [GameInfo(game_id=game_id.text.strip().replace('/', ''), game_date=game_date) for game_id in game_ids]


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


def get_season_hitter_pitch_stats(player_id, game_info):
    """
    Get a dictionary of the season hitter tendencies represented by outs recorded
    :param player_id: Gameday player ID of hitter of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_date: game date
    :return: dictionary of the season hitter tendencies represented by outs recorded
    """

    try:
        url = BASE_URL + 'year_' + str(game_info.game_date.year) + '/' + 'month_' + int_to_two_digits(game_info.game_date.month) + '/' + 'day_' + \
              int_to_two_digits(game_info.game_date.day)

        # Get the batters URL
        season_dict = dict()
        batters_url = url + '/' + game_info.game_id + '/premium/batters/' + player_id + '/'
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


def get_season_pitcher_pitch_stats(player_id, game_info):
    """
    Get a dictionary of the season pitcher tendencies represented by outs recorded
    :param player_id: Gameday player ID of pitcher of interest
    :param team_abbrev: Gameday team abbreviation
    :param game_info: game date
    :return: dictionary of the season pitcher tendencies represented by outs recorded
    """
    try:
        url = BASE_URL + 'year_' + str(game_info.game_date.year) + '/' + 'month_' + int_to_two_digits(game_info.game_date.month) + '/' + 'day_' + \
              int_to_two_digits(game_info.game_date.day)

        # Get the batters URL
        season_dict = dict()
        pitchers_url = url + '/' + game_info.game_id + 'premium/pitchers/' + player_id + '/'
        # Changeups
        soup = get_soup_from_url(pitchers_url + 'pch.xml')
        season_dict['ch'] = soup.find('std').find('sit').attrs
        # Curveball
        soup = get_soup_from_url(pitchers_url + 'pcu.xml')
        season_dict['cu'] = soup.find('std').find('sit').attrs
        #
        soup = get_soup_from_url(pitchers_url + 'pfa.xml')
        season_dict['fa'] = soup.find('std').find('sit').attrs
        # Cutter
        soup = get_soup_from_url(pitchers_url + 'pfc.xml')
        season_dict['fc'] = soup.find('std').find('sit').attrs
        # Four-seam fastball
        soup = get_soup_from_url(pitchers_url + 'pff.xml')
        season_dict['ff'] = soup.find('std').find('sit').attrs
        #
        soup = get_soup_from_url(pitchers_url + 'pfs.xml')
        season_dict['fs'] = soup.find('std').find('sit').attrs
        # Two-seam fastball?
        soup = get_soup_from_url(pitchers_url + 'pft.xml')
        season_dict['ft'] = soup.find('std').find('sit').attrs
        # Knuckleball
        soup = get_soup_from_url(pitchers_url + 'pkn.xml')
        season_dict['kn'] = soup.find('std').find('sit').attrs
        # Sinker
        soup = get_soup_from_url(pitchers_url + 'psi.xml')
        season_dict['si'] = soup.find('std').find('sit').attrs
        # Slider
        soup = get_soup_from_url(pitchers_url + 'psl.xml')
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
    game_ids = get_game_ids(game_date)
    # Find the relevant team in list of URLS
    matching_game_id = [game_id for game_id in game_ids if team_abbrev in game_id]

    # Get the pitcher's URL
    game_dict = dict()
    batters_url = url + '/' + matching_game_id[0] + 'premium/pitchers/' + player_id + '/'
    #
    soup = get_soup_from_url(batters_url + 'pitchtendencies_game.xml')

    game_pitch_types = soup.find('std').find('types').findAll('type')
    for game_pitch_type in game_pitch_types:
        game_dict[game_pitch_type.attrs['id']] = game_pitch_type.attrs

    return game_dict


def get_all_game_urls(game_date):
    url = BASE_URL + 'year_' + str(game_date.year) + '/' + 'month_' + int_to_two_digits(
        game_date.month) + '/' + 'day_' + \
          int_to_two_digits(game_date.day)


class PregameStats(object):
    def __init__(self):
        self.team = None
        self.season_stats_dict = None
        self.career_stats_dict = None
        self.month_stats_dict = None
        self.team_stats_dict = None
        self.bases_empty_stats_dict = None
        self.men_on_stats_dict = None
        self.risp_stats_dict = None
        self.bases_loaded_stats_dict = None
        self.vs_lhp_stats_dict = None
        self.vs_rhp_stats_dict = None


class PitchStats(object):
    def __init__(self):
        self.pitch_dict = dict()


class PitcherGameStats(object):
    def __init__(self):
        self.id = None
        self.pregame_stats = PregameStats()
        self.pitch_stats = PitchStats()


class HitterGameStats(object):
    def __init__(self):
        self.id = None
        self.batting_order_position = None
        self.pregame_stats = PregameStats()
        self.pitch_stats = PitchStats()


class Umpire(object):
    def __init__(self):
        self.name = None
        self.id = None


class GameAttributes(object):
    def __init__(self):
        self.id_info = None
        self.umpire = list()
        self.game_time = None
        self.home_team = None
        self.away_team = None
        self.temperature = None
        self.wind_speed = None
        self.wind_description = None
        self.weather_condition = None


def get_game_hitter_stats(soup):
    """
    Get all stats for a particular hitter before the game
    :param soup:
    :return:
    """
    root_xml = soup.find('player')

    hitter_game_stats = None
    if len(root_xml.find('atbats').findAll('ab')) > 0:
        hitter_game_stats = PregameStats()
        hitter_game_stats.team = root_xml.attrs['team']
        hitter_game_stats.season_stats_dict = root_xml.find('season').attrs
        hitter_game_stats.career_stats_dict = root_xml.find('career').attrs
        hitter_game_stats.month_stats_dict = root_xml.find('month').attrs
        hitter_game_stats.team_stats_dict = root_xml.find('team').attrs
        hitter_game_stats.bases_empty_stats_dict = root_xml.find('empty').attrs
        hitter_game_stats.men_on_stats_dict = root_xml.find('men_on').attrs
        hitter_game_stats.risp_stats_dict = root_xml.find('risp').attrs
        hitter_game_stats.bases_loaded_stats_dict = root_xml.find('loaded').attrs
        hitter_game_stats.vs_lhp_stats_dict = root_xml.find('vs_lhp').attrs
        hitter_game_stats.vs_rhp_stats_dict = root_xml.find('vs_rhp').attrs

    # TODO: figure out how to get stats versus this pitcher. may need to just look at all games

    return hitter_game_stats


def get_hitter_ids(game_id_info):
    url = BASE_URL + 'year_' + str(game_id_info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            game_id_info.game_date.month) + '/' + 'day_' + \
            int_to_two_digits(game_id_info.game_date.day) + '/' + game_id_info.game_id + '/batters/'
    soup = get_soup_from_url(url)
    batter_ids = soup.select("a[href*=.xml]")
    return [batter_id.text.strip() for batter_id in batter_ids]


def get_game_pitcher_stats(soup):
    """
    Get all stats for a particular hitter before the game
    :param soup:
    :return:
    """
    root_xml = soup.find('player')

    pitcher_game_stats = PregameStats()
    pitcher_game_stats.team = root_xml.attrs['team']
    pitcher_game_stats.season_stats_dict = root_xml.find('season').attrs
    pitcher_game_stats.career_stats_dict = root_xml.find('career').attrs
    pitcher_game_stats.month_stats_dict = root_xml.find('month').attrs
    pitcher_game_stats.team_stats_dict = root_xml.find('team').attrs
    pitcher_game_stats.bases_empty_stats_dict = root_xml.find('empty').attrs
    pitcher_game_stats.men_on_stats_dict = root_xml.find('men_on').attrs
    pitcher_game_stats.risp_stats_dict = root_xml.find('risp').attrs
    pitcher_game_stats.bases_loaded_stats_dict = root_xml.find('loaded').attrs
    pitcher_game_stats.vs_lhp_stats_dict = root_xml.find('vs_lhp').attrs
    pitcher_game_stats.vs_rhp_stats_dict = root_xml.find('vs_rhp').attrs

    return pitcher_game_stats


def get_pitcher_ids(game_id_info):
    url = BASE_URL + 'year_' + str(game_id_info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            game_id_info.game_date.month) + '/' + 'day_' + \
            int_to_two_digits(game_id_info.game_date.day) + '/' + game_id_info.game_id + '/pitchers/'
    soup = get_soup_from_url(url)
    pitcher_ids = soup.select("a[href*=.xml]")
    return [pitcher_id.text.strip() for pitcher_id in pitcher_ids]


def get_game_batting_orders(game_id_info):
    # TODO: make sure this is correct and this is not the state of the lineup at the END of the game

    url = BASE_URL + 'year_' + str(game_id_info.game_date.year) + '/' + 'month_' + int_to_two_digits(
        game_id_info.game_date.month) + '/' + 'day_' + \
          int_to_two_digits(game_id_info.game_date.day) + '/' + game_id_info.game_id + '/plays.xml'
    soup = get_soup_from_url(url)
    teams_xml = soup.find('game').find('lineup').findAll('team')
    home_team_order = list()
    away_team_order = list()
    for team_xml in teams_xml:
        if team_xml.attrs['type'] == 'home':
            team = team_xml.findAll('man')
            for player in team:
                home_team_order.append(player.attrs['pid'])
        else:
            team = team_xml.findAll('man')
            for player in team:
                away_team_order.append(player.attrs['pid'])

    return home_team_order, away_team_order


def mine_hitter_stats(game_id_info):

    hitter_stat_list = list()
    for info in game_id_info:
        hitter_ids = get_hitter_ids(info)
        home_batting_order, away_batting_order = get_game_batting_orders(info)
        for hitter_id in hitter_ids:
            hitter_url = BASE_URL + 'year_' + str(info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            info.game_date.month) + '/' + 'day_' + \
            int_to_two_digits(info.game_date.day) + '/' + info.game_id + '/batters/' + hitter_id

            hitter_soup = get_soup_from_url(hitter_url)

            hitter_id_str = hitter_id.split('.')[0]
            hitter_stats = HitterGameStats()
            hitter_stats.pregame_stats = get_game_hitter_stats(hitter_soup)
            if hitter_stats.pregame_stats is not None:
                hitter_stats.pitch_stats = get_season_hitter_pitch_stats(hitter_id_str, info)
                for i in range(0, len(home_batting_order)):
                    if home_batting_order[i] == hitter_id_str:
                        hitter_stats.batting_order_position = i
                        break
                for i in range(0, len(away_batting_order)):
                    if away_batting_order[i] == hitter_id_str:
                        hitter_stats.batting_order_position = i
                        break
                if hitter_stats.batting_order_position is not None:
                    hitter_stats.id = hitter_id_str
                    hitter_stat_list.append(hitter_stats)

    return hitter_stat_list


def mine_game_attributes(game_id_info):
    game_attribute_list = list()

    for info in game_id_info:
        game_attributes = GameAttributes()

        # Get the game time
        url = BASE_URL + 'year_' + str(info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            info.game_date.month) + '/' + 'day_' + \
              int_to_two_digits(info.game_date.day) + '/' + info.game_id + '/game.xml'
        soup = get_soup_from_url(url)
        game_attributes.game_time = soup.find('game').attrs['local_game_time']
        teams_xml = soup.find('game').findAll('team')
        for team_xml in teams_xml:
            if team_xml.attrs['type'] == 'home':
                game_attributes.home_team = team_xml.attrs['abbrev']
            else:
                game_attributes.away_team = team_xml.attrs['abbrev']

        # Get information about the umpire
        url = BASE_URL + 'year_' + str(info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            info.game_date.month) + '/' + 'day_' + \
              int_to_two_digits(info.game_date.day) + '/' + info.game_id + '/players.xml'
        soup = get_soup_from_url(url)

        umpires_xml = soup.find('game').find('umpires').findAll('umpire')
        for umpire_xml in umpires_xml:
            if umpire_xml.attrs['position'] == 'home':
                game_attributes.umpire = Umpire()
                game_attributes.umpire.id = umpire_xml.attrs['id']
                game_attributes.umpire.name = umpire_xml.attrs['name']

        # Get the weather characteristics
        # TODO: how do we know if we're in a dome?
        url = BASE_URL + 'year_' + str(info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            info.game_date.month) + '/' + 'day_' + \
              int_to_two_digits(info.game_date.day) + '/' + info.game_id + '/plays.xml'
        soup = get_soup_from_url(url)
        weather_xml = soup.find('game').find('weather')
        game_attributes.temperature = int(weather_xml.attrs['temp'].strip())
        game_attributes.weather_condition = weather_xml.attrs['condition']
        game_attributes.wind_speed = int(weather_xml.attrs['wind'].split('mph')[0].strip())
        game_attributes.wind_description = weather_xml.attrs['wind'].split('mph')[1].strip()

        game_attributes.id_info = info
        game_attribute_list.append(game_attributes)

    return game_attribute_list


def mine_pitcher_stats(game_id_info):

    pitcher_stat_list = list()
    for info in game_id_info:
        pitcher_ids = get_pitcher_ids(info)
        for pitcher_id in pitcher_ids:
            pitcher_url = BASE_URL + 'year_' + str(info.game_date.year) + '/' + 'month_' + int_to_two_digits(
            info.game_date.month) + '/' + 'day_' + \
            int_to_two_digits(info.game_date.day) + '/' + info.game_id + '/pitchers/' + pitcher_id

            pitcher_soup = get_soup_from_url(pitcher_url)

            pitcher_id_str = pitcher_id.split('.')[0]
            pitcher_stats = PitcherGameStats()
            pitcher_stats.pregame_stats = get_game_pitcher_stats(pitcher_soup)
            if pitcher_stats.pregame_stats is not None:
                pitcher_stats.pitch_stats = get_season_pitcher_pitch_stats(pitcher_id_str, info)
                pitcher_stats.id = pitcher_id_str
                pitcher_stat_list.append(pitcher_stats)

    return pitcher_stat_list


def mine_games(game_date):
    game_id_info = get_game_ids(game_date)
    game_list = mine_game_attributes(game_id_info)
    hitter_stat_list = mine_hitter_stats(game_id_info)
    pitcher_stat_list = mine_pitcher_stats(game_id_info)

    return game_list, hitter_stat_list, pitcher_stat_list
