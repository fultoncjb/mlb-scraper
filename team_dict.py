import bidict

# Two-way dictionary
rotowire_team_dict = bidict.bidict(ARI="Arizona Diamondbacks",
                          ATL="Atlanta Braves",
                          BAL="Baltimore Orioles",
                          BOS="Boston Red Sox",
                          CHC="Chicago Cubs",
                          CWS="Chicago White Sox",
                          CIN="Cincinnati Reds",
                          CLE="Cleveland Indians",
                          COL="Colorado Rockies",
                          DET="Detroit Tigers",
                          HOU="Houston Astros",
                          KC="Kansas City Royals",
                          LAA="Los Angeles Angels",
                          LAD="Los Angeles Dodgers",
                          MIA="Miami Marlins",
                          MIL="Milwaukee Brewers",
                          MIN="Minnesota Twins",
                          NYM="New York Mets",
                          NYY="New York Yankees",
                          OAK="Oakland Athletics",
                          PHI="Philadelphia Phillies",
                          PIT="Pittsburgh Pirates",
                          SD="San Diego Padres",
                          SEA="Seattle Mariners",
                          SF="San Francisco Giants",
                          STL="St. Louis Cardinals",
                          TB="Tampa Bay Rays",
                          TEX="Texas Rangers",
                          TOR="Toronto Blue Jays",
                          WAS="Washington Nationals")

# Two-way dictionary
baseball_reference_team_dict = bidict.bidict(ARI="Arizona Diamondbacks",
                          ATL="Atlanta Braves",
                          BAL="Baltimore Orioles",
                          BOS="Boston Red Sox",
                          CHC="Chicago Cubs",
                          CHW="Chicago White Sox",
                          CIN="Cincinnati Reds",
                          CLE="Cleveland Indians",
                          COL="Colorado Rockies",
                          DET="Detroit Tigers",
                          HOU="Houston Astros",
                          KCR="Kansas City Royals",
                          LAA="Los Angeles Angels of Anaheim",
                          #LAA="Los Angeles Angels",
                          LAD="Los Angeles Dodgers",
                          MIA="Miami Marlins",
                          MIL="Milwaukee Brewers",
                          MIN="Minnesota Twins",
                          NYM="New York Mets",
                          NYY="New York Yankees",
                          OAK="Oakland Athletics",
                          PHI="Philadelphia Phillies",
                          PIT="Pittsburgh Pirates",
                          SDP="San Diego Padres",
                          SEA="Seattle Mariners",
                          SFG="San Francisco Giants",
                          STL="St. Louis Cardinals",
                          TBR="Tampa Bay Rays",
                          TEX="Texas Rangers",
                          TOR="Toronto Blue Jays",
                          WSN="Washington Nationals")

fan_graph_team_dict = bidict.bidict(ARI="diamondbacks",
                                    ATL="braves",
                                    BAL="orioles",
                                    BOS="red-sox",
                                    CHC="cubs",
                                    CHW="white-sox",
                                    CIN="reds",
                                    CLE="guardians",
                                    COL="rockies",
                                    DET="tigers",
                                    HOU="astros",
                                    KCR="royals",
                                    LAA="angels",
                                    LAD="dodgers",
                                    MIA="marlins",
                                    MIL="brewers",
                                    MIN="twins",
                                    NYM="mets",
                                    NYY="yankees",
                                    OAK="athletics",
                                    PHI="phillies",
                                    PIT="pirates",
                                    SDP="padres",
                                    SEA="mariners",
                                    SFG="giants",
                                    STL="cardinals",
                                    TBR="rays",
                                    TEX="rangers",
                                    TOR="blue-jays",
                                    WSN="nationals")


def get_baseball_reference_team(full_team_name):
    """
    Get the Baseball Reference abbreviation from the Rotowire abbreviation
    :param full_team_name: team name in the Rotowire dictionary
    :return: Baseball Reference team abbreviation
    """
    if rotowire_team_dict[full_team_name] == "Los Angeles Angels":
        team = baseball_reference_team_dict.inv["Los Angeles Angels of Anaheim"]
    else:
        team = baseball_reference_team_dict.inv[rotowire_team_dict[full_team_name]]

    return team
