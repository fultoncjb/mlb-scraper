# mlb-scraper
mlb-scraper is a Python package for scraping MLB Stats. The package makes heavy use of BeautifulSoup as the scraping engine.

[![Build Status](https://app.travis-ci.com/fultoncjb/mlb-scraper.svg?branch=master)](https://app.travis-ci.com/fultoncjb/mlb-scraper)

#### Support

Buy me a coffee to acclerate further development

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/fultoncjb)

#### Installation Instructions
* Download the latest release and unpack it to your local directory.
* From the latest release folder, run the following commands:
```
pip install .
```

#### Quick Example
Suppose you are interested in how many hits David Ortiz had in 2013. The below snippet illustrates how to achieve this using the API:

``` 
from stat_miner import *
hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2010)
hitter_miner = HitterMiner(hitter_id)
season_stats = hitter_miner.mine_season_stats(2013)
print season_stats["H"] 
```
Note that the HitterMiner is dependent on a unique identifier derived from the name of the player, the player's team, and the year. The team and year represent a season the player was on a given team, making it easier to locate the player's unique identifier.

Similarly, this can be done with pitchers. Suppose you are interested in how many strikeouts Pedro Martinez had in 1999. The below snippet illustrates how to achieve this using the API:

```
from stat_miner import *
pitcher_id = PitcherMiner.get_id("Pedro Martinez", "BOS", 2001)
pitcher_miner = PitcherMiner(pitcher_id)
season_stats = pitcher_miner.mine_season_stats(1999)
print season_stats["SO"]
```

