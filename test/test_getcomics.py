#!/usr/bin/python3
# -*-coding:utf-8 -*-

import unittest
from utils.getcomics import findLastWeekly
from utils.getcomics import comicsList


class TestFonctionGet(unittest.TestCase):

    getcomicsurls = ['https://getcomics.info/tag/dc-week/',
                     'http://getcomics.info/tag/marvel-now/',
                     'https://getcomics.info/tag/indie-week/',
                     'https://getcomics.info/tag/image-week/'
                     ]

    # Chaque méthode dont le nom commence par 'test_'
    # est un test.
    def test_findLastWeekly_DC(self):

        # result = 'https://getcomics.info/dc/2019-02-27-dc-week/'

        myurl = findLastWeekly(self.getcomicsurls[0])

        print(myurl)

        # Le test le plus simple est un test d'égalité. On se
        # sert de la méthode assertEqual pour dire que l'on
        # s'attend à ce que les deux éléments soient égaux. Sinon
        # le test échoue.
        # self.assertEqual(myurl, result)

    def test_findLastWeekly_Marvel(self):

        # result = 'https://getcomics.info/marvel/2019-02-27-marvel-week/'

        myurl = findLastWeekly(self.getcomicsurls[1])

        print(myurl)

        # self.assertEqual(myurl, result)

    def test_findLastWeekly_Indie(self):

        # result = 'https://getcomics.info/other-comics/2019-02-27-indie-week/'

        myurl = findLastWeekly(self.getcomicsurls[2])

        print(myurl)

        # self.assertEqual(myurl, result)

    def test_findLastWeekly_Image(self):

        # result = 'https://getcomics.info/other-comics/2019-02-27-image-week/'

        myurl = findLastWeekly(self.getcomicsurls[3])

        print(myurl)

        # self.assertEqual(myurl, result)

    def test_comicsList(self):
        print("Comics list DC")
        result = comicsList(self.getcomicsurls[0])
        print(result)


# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    unittest.main()
