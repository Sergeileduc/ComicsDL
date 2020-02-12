#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/zpshare."""

# import pytest
from utils.zpshare import (get_file_url, _remove_tag,
                           find_zippy_download_button)
# from utils import htmlsoup


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
