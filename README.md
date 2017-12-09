# mlb-scraper
mlb-scraper is a Python package for scraping MLB Stats. The package makes heavy use of BeautifulSoup as the scraping engine.

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

