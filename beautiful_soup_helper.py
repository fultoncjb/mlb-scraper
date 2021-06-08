"""
beautiful_soup_helper.py
Module used for implementing some wrapper functions for BeautifulSoup
"""

from bs4 import BeautifulSoup, Comment
import requests
from datetime import date


class Http404Exception(Exception):

    def __init__(self, invalid_url):
        super(Http404Exception, self).__init__("Attempt to access invalid URL %s." % invalid_url)


def str_to_date(date_string):
    """ Convert a PitchFx date string to a Date object
    :param date_string: a PitchFx date string
    :return the Date object representing the string
    """
    date_members = date_string.split("/")
    date_object = date(int(date_members[0]), int(date_members[1]), int(date_members[2]))
    return date_object


def url_to_comment_soup(url):
    """ In order to mine JavaScript, mine the comments
    :param url: the absolute URL string
    :return: the BeautifulSoup object containing the comments, return None if the object was not
    successfully created
    """
    response = requests.get(url)

    if response.status_code == 404:
        print("Attempt to access invalid URL: " + response.url)
        raise Http404Exception(url)

    soup_initial = BeautifulSoup(response.text, "lxml")
    soup_comments = soup_initial.findAll(text=lambda text: isinstance(text, Comment))
    soup = str()
    for soup_comment in soup_comments:
        soup += soup_comment

    return BeautifulSoup(soup, "lxml")


def url_to_soup(url):
    """ Take a URL and get the BeautifulSoup object
    :param url: the absolute URL string
    :return the BeautifulSoup object returned, return None if the object was not successfully created
    """
    response = requests.get(url)

    if response.status_code == 404:
        print("Attempt to access invalid URL: " + response.url)
        raise Http404Exception(url)

    return BeautifulSoup(response.text, "lxml")


def get_soup_from_url(url):
    for i in range(5):
        try:
            soup = url_to_soup(url)
        except IOError:
            print("Socket error. Trying to obtain soup again.")
            continue
        except Http404Exception:
            return None

        return soup

    print("Exhausted all attempts to get the soup. Check your internet connection.")
    assert 0


def get_comment_soup_from_url(url):
    for i in range(5):
        try:
            soup = url_to_comment_soup(url)
        except IOError:
            print("Socket error. Trying to obtain soup again.")
            continue
        except Http404Exception:
            return None

        return soup

    print("Exhausted all attempts to get the soup. Check your internet connection.")
    assert 0

