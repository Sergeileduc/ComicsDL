#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests for utils/getcomics."""

import unittest
from utils.getcomics import find_last_weekly, comics_list
from utils.getcomics import searchurl, getresults


class TestFonctionGet(unittest.TestCase):
    """Tests for getcomics module."""

    getcomicsurls = ['https://getcomics.info/tag/dc-week/',
                     'http://getcomics.info/tag/marvel-now/',
                     'https://getcomics.info/tag/indie-week/',
                     'https://getcomics.info/tag/image-week/'
                     ]

    # Chaque méthode dont le nom commence par 'test_'
    # est un test.
    def test_find_last_weekly_DC(self):
        """Test find_last_weekly."""
        myurl = find_last_weekly(self.getcomicsurls[0])
        print(myurl)

        # Le test le plus simple est un test d'égalité. On se
        # sert de la méthode assertEqual pour dire que l'on
        # s'attend à ce que les deux éléments soient égaux. Sinon
        # le test échoue.
        # self.assertEqual(myurl, result)

    def test_find_last_weekly_marvel(self):
        """Test find_last_weekly."""
        myurl = find_last_weekly(self.getcomicsurls[1])
        print(myurl)
        # self.assertEqual(myurl, result)

    def test_find_last_weekly_indie(self):
        """Test find_last_weekly."""
        myurl = find_last_weekly(self.getcomicsurls[2])
        print(myurl)
        # self.assertEqual(myurl, result)

    def test_find_last_weekly_image(self):
        """Test find_last_weekly."""
        myurl = find_last_weekly(self.getcomicsurls[3])
        print(myurl)
        # self.assertEqual(myurl, result)

    def test_comicsList(self):
        """Test comics_list()."""
        print("Comics list DC")
        result = comics_list(self.getcomicsurls[0])
        print(result)

    def test_searchurl_1(self):
        """Test searchurl()."""
        myurl = searchurl("Batman", 0, 2)
        expected = "https://getcomics.info/tag/batman/page/2/"
        print(myurl)
        self.assertEqual(myurl, expected)

    def test_searchurl_2(self):
        """Test searchurl()."""
        myurl = searchurl("New X-Men", 1, 3)
        expected = "https://getcomics.info/page/3/?s=new+x-men"
        print(myurl)
        self.assertEqual(myurl, expected)

    def test_get_results(self):
        """Test getresults."""
        searchurl = "https://getcomics.info/tag/batman/page/2/"
        searchlist = getresults(searchurl)
        print(searchlist)


# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    unittest.main()
