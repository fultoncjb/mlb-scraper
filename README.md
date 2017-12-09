# mlb-scraper
mlb-scraper is a Python package for scraping MLB Stats. The package makes heavy use of BeautifulSoup as the scraping engine.

# Season Hitting Stats
Suppose you are interested in how many hits David Ortiz had in 2013. The below snippet illustrates how to achieve this using the API:

from stat_miner import *
hitter_id = HitterMiner.get_id("David Ortiz", "BOS", 2013)
hitter_miner = HitterMiner(hitter_id)
season_stats = hitter_miner.mine_season_stats(2013)
print season_stats["H"]
