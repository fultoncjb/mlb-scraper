
from rotowire import SeleniumRotowireMiner
from unittest import TestCase


class RotowireTest(TestCase):

    def test_get_game_lineups(self):
        miner = SeleniumRotowireMiner()
        game_lineups = miner.get_game_lineups()
        self.assertTrue(len(game_lineups) > 0)