#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/getcomics."""

import pytest

from utils.getcomics import find_last_weekly, comics_list
from utils.getcomics import searchurl, getresults


@pytest.fixture(scope="module",
                params=['https://getcomics.info/tag/dc-week/',
                        'http://getcomics.info/tag/marvel-now/',
                        'https://getcomics.info/tag/indie-week/',
                        'https://getcomics.info/tag/image-week/'
                        ])
def getcomics_url(request):
    return request.param


def test_find_last_weekly(getcomics_url):
    """Test find_last_weekly."""
    myurl = find_last_weekly(getcomics_url)
    print(myurl)
    assert myurl is not None


def test_comicsList(getcomics_url):
    """Test comics_list()."""
    result = comics_list(getcomics_url)
    print(result)
    assert result is not None


@pytest.mark.parametrize(
    "input_,mode,page,expected",
    [("Batman", 0, 2, "https://getcomics.info/tag/batman/page/2/"),
     ("New X-Men", 1, 3, "https://getcomics.info/page/3/?s=new+x-men")])
def test_searchurl(input_, mode, page, expected):
    myurl = searchurl(input_, mode, page)
    assert myurl == expected


def test_get_results():
    """Test getresults."""
    searchurl = "https://getcomics.info/tag/batman/page/2/"
    searchlist = getresults(searchurl)
    print(searchlist)
