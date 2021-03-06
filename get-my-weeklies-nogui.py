#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Download selected comics in getcomics.info weekly packs."""

import os
import sys
import time

from utils.getcomics import get_weekly_comics

myComicsList = []

config = 'liste-comics.txt'

# Read configfile
try:
    configfile = os.path.join(os.path.dirname(__file__), config)
    userList = list()
    with open(configfile, 'r') as f:
        userList = f.read().splitlines()
        userList.sort()
        f.close()
    with open(configfile, 'w') as f:
        for comic in userList:
            f.write(f'{comic}\n')
            myComicsList.append(comic.lower().replace(' ', '-'))
        f.close()
except IOError:
    print(f"Erreur : Il faut créer un fichier {config}"
          " et y ajouter vos séries en ligne,\n comme par exemple"
          "\n.........\nBatman\nSuperman\nInjustice\netc...\n.........")
    sys.exit(1)

try:
    get_weekly_comics(myComicsList)
    time.sleep(20)
except NameError as e:
    print(e)
    print("Le script a rencontré une erreur.\nVous pouvez fermer.")
    time.sleep(20)
