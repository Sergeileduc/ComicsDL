#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/zpshare."""

import pandas as pd
import pytest
from utils.tools import search_regex_name
from utils.zpshare import (get_file_url, _remove_tag,
                           find_zippy_download_button,
                           regex_abcd)
# from utils import htmlsoup


# Read abcd from file and make a list of tuples
df = pd.read_csv('tests/test_zpshare/expected_abcd.csv', header=None)
abcd = [tuple(row) for row in df.values]
#  = [('a', 45372), ('b', 51245), ('c', 45372), ('d', 913)]


@pytest.fixture
def button_html(datadir):
    contents = (datadir / 'button_script.txt').read_text()
    return contents


@pytest.mark.parametrize("field,expected", abcd)
def test_search_regex_name(button_html, field, expected):
    """Doc."""
    print("youhu")
    res = int(search_regex_name(button_html, regex_abcd, field))
    assert res == expected


def test_get_file_url():
    """Test get_file_url()."""
    # url = "https://www4.zippyshare.com/v/tbiaf4on/file.html"
    url = "https://www90.zippyshare.com/v/T3CXRVue/file.html"

    ref = "Batman 088 (2020).cbr"

    down_button = find_zippy_download_button(url)

    _, name = get_file_url(url, down_button)
    # print("--------------------------------------")
    # print(name)
    assert ref == name


def test_remove_tag():
    """Test remove tag."""
    old_name = ("Doomsday Clock 09 (of 12) (2019) (Webrip) "
                "(The Last Kryptonian-DCP).cbr")

    valid_name = "Doomsday Clock 09 (of 12) (2019).cbr"

    new_name = _remove_tag(old_name)

    assert valid_name == new_name
