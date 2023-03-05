#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/zpshare."""

import pandas as pd
import pytest
from utils.tools import search_regex_name
from utils.zpshare import (get_file_url, _remove_tag,
                           find_zippy_download_button,
                           regex_abcd)


# This way of comuting URL is DEPRECATED for the moment
# Read abcd from file and make a list of tuples
df = pd.read_csv('tests/test_zpshare/expected_abcd.csv', header=None)
abcd = [tuple(row) for row in df.values]
#  = [('a', 45372), ('b', 51245), ('c', 45372), ('d', 913)]


@pytest.fixture
def button_html(datadir):
    contents = (datadir / 'button_script.txt').read_text()
    return contents


@pytest.mark.deprecated("This way of finding URL with a b c d values is DEPRECATED")
@pytest.mark.parametrize("field,expected", abcd)
def test_search_regex_name(button_html, field, expected):
    """Doc."""
    res = int(search_regex_name(button_html, regex_abcd, field))
    assert res == expected


@pytest.mark.parametrize("url,expected_name",
                         [("https://www90.zippyshare.com/v/T3CXRVue/file.html",
                           "Batman 088 (2020).cbr")])
def test_get_file_url(url, expected_name):
    """Test get_file_url()."""
    down_button = find_zippy_download_button(url)
    _, name = get_file_url(url, down_button)
    assert name == expected_name


@pytest.mark.parametrize("old_name,new_name",
                         [("Doomsday Clock 09 (of 12) (2019) (Webrip) (The Last Kryptonian-DCP).cbr",  # noqa: E501
                           "Doomsday Clock 09 (of 12) (2019).cbr")])
def test_remove_tag(old_name, new_name):
    """Test remove tag."""
    remove_tag_name = _remove_tag(old_name)
    assert remove_tag_name == new_name
