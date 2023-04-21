
#!/usr/bin/env python

from distutils.core import setup

setup(name='mlbscrape',
      version='1.0.1',
      description='Python package for mining MLB data',
      url='https://github.com/fultoncjb/mlb-scraper',
      py_modules=['baseball_reference', 'stat_miner', 'rotowire', 'draft_kings', 'team_dict', 'beautiful_soup_helper', 'fan_graphs'],
      install_requires=['bidict', 'bs4', 'lxml', 'requests', 'selenium', 'pyyaml']
     )
