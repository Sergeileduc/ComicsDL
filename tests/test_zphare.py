#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/zpshare."""

import unittest
from utils.zpshare import get_file_url, _remove_tag, find_zippy_download_button
# from utils import htmlsoup


class TestFonctionGet(unittest.TestCase):
    """Tests for zpshare module."""

    # Chaque méthode dont le nom commence par 'test_'
    # est un test.
    def test_get_file_url(self):
        """Test get_file_url()."""
        url = "https://www4.zippyshare.com/v/tbiaf4on/file.html"

        ref = "Batman v3 066 (2019).cbr"

        down_button = find_zippy_download_button(url)

        _, name = get_file_url(url, down_button)
        # print("--------------------------------------")
        # print(name)
        # print(out_url)
        self.assertEqual(ref, name)

    def test_remove_tag(self):
        """Test remove tag."""
        old_name = ("Doomsday Clock 09 (of 12) (2019) (Webrip) "
                    "(The Last Kryptonian-DCP).cbr")

        valid_name = "Doomsday Clock 09 (of 12) (2019).cbr"

        new_name = _remove_tag(old_name)

        self.assertEqual(valid_name, new_name)


# This will launch test if executed.
if __name__ == '__main__':
    unittest.main()
