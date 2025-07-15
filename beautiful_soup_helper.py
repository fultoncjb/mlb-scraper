"""
beautiful_soup_helper.py
Module used for implementing some wrapper functions for BeautifulSoup
"""

from bs4 import BeautifulSoup, Comment
import requests
from datetime import date
from time import sleep


class Http404Exception(Exception):

    def __init__(self, invalid_url):
        super(Http404Exception, self).__init__("Attempt to access invalid URL %s." % invalid_url)


class Http429Exception(Exception):

    def __init__(self, url):
        super(Http429Exception, self).__init__("Rate limit reached when accessing URL %s" % url)


class HttpGeneralException(Exception):

    def __init__(self, status_code, url):
        super(HttpGeneralException, self).__init__("Received bad status code %i for URL %s" % (status_code, url))


class Http522Exception(Exception):

    def __init__(self, url):
        super(Http522Exception, self).__init__("Could not establish TCP connection for URL %s" % url)


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
    elif response.status_code == 429:
        print("Rate limit reached!")
        raise Http429Exception(url)
    elif response.status_code != 200:
        raise HttpGeneralException(response.status_code, url)

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
    elif response.status_code == 429:
        print("Rate limit reached!")
        raise Http429Exception(url)
    elif response.status_code == 522:
        print("Could not establish TCP comms")
        raise Http522Exception(url)
    elif response.status_code != 200:
        raise HttpGeneralException(response.status_code, url)

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

