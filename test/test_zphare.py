#!/usr/bin/python3
# -*-coding:utf-8 -*-

import unittest
from utils.zpshare import getFileUrl


class TestFonctionGet(unittest.TestCase):

    # Chaque méthode dont le nom commence par 'test_'
    # est un test.
    def test_getFileUrl(self):

        url = "https://www4.zippyshare.com/v/tbiaf4on/file.html"

        f = open("zippy_button_script.txt", "r")
        button = f.read()
        f.close()

        # result = 'https://getcomics.info/dc/2019-02-27-dc-week/'

        name, out_url = getFileUrl(url, button)
        print(name)
        print(out_url)

        # Le test le plus simple est un test d'égalité. On se
        # sert de la méthode assertEqual pour dire que l'on
        # s'attend à ce que les deux éléments soient égaux. Sinon
        # le test échoue.
        # self.assertEqual(myurl, result)


# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    unittest.main()
