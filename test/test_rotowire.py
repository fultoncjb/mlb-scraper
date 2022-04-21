
from rotowire import SeleniumMiner
from unittest import TestCase


class RotowireTest(TestCase):

    def test_get_game_lineups(self):
        miner = SeleniumMiner()
        game_lineups = miner.get_game_lineups()
        print("Blah")