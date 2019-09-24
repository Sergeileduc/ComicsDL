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

        down_button = find_zippy_download_button(url)

        name, out_url = get_file_url(url, down_button)
        print("--------------------------------------")
        print(name)
        print(out_url)

        # Le test le plus simple est un test d'égalité. On se
        # sert de la méthode assertEqual pour dire que l'on
        # s'attend à ce que les deux éléments soient égaux. Sinon
        # le test échoue.
        # self.assertEqual(myurl, result)

    def test_remove_tag(self):
        """Test remove tag."""
        print("Test removetag")
        old_name = "Doomsday Clock 09 (of 12) (2019) (Webrip) " \
                   "(The Last Kryptonian-DCP).cbr"

        valid_name = "Doomsday Clock 09 (of 12) (2019).cbr"

        new_name = _remove_tag(old_name)

        self.assertEqual(valid_name, new_name)


# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    unittest.main()
