#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/zpshare."""

import pandas as pd
import pytest
from utils.tools import search_regex_name
from utils.zpshare import get_file_filename_url, _remove_tag


# Read abcd from file and make a list of tuples
df = pd.read_csv('tests/test_zpshare/expected_abcd.csv', header=None)
abcd = [tuple(row) for row in df.values]
#  = [('a', 45372), ('b', 51245), ('c', 45372), ('d', 913)]


@pytest.fixture
def button_html(datadir):
    contents = (datadir / 'button_script.txt').read_text()
    return contents


@pytest.mark.deprecated("This test is no longer required")
@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.parametrize("field,expected", abcd)
def test_search_regex_name(button_html, field, expected):
    """Doc."""
    regex_abcd = r'.*?getElementById.*?href = \"(.*?)\" \+ \((?P<a>\d+) \% (?P<b>\d+) \+ (?P<c>\d+) \% (?P<d>\d+)\)'  # noqa: E501
    res = int(search_regex_name(button_html, regex_abcd, field))
    assert res == expected


@pytest.mark.parametrize("url,expected_name",
                         [("https://www32.zippyshare.com/v/gIpN3vBt/file.html",
                           "X-Force 038 (2023).cbr")])
def test_get_file_url(url, expected_name):
    """Test get_file_url()."""
    _, name = get_file_filename_url(url)
    assert name == expected_name


@pytest.mark.parametrize("old_name,new_name",
                         [("Doomsday Clock 09 (of 12) (2019) (Webrip) (The Last Kryptonian-DCP).cbr",  # noqa: E501
                           "Doomsday Clock 09 (of 12) (2019).cbr")])
def test_remove_tag(old_name, new_name):
    """Test remove tag."""
    remove_tag_name = _remove_tag(old_name)
    assert remove_tag_name == new_name
