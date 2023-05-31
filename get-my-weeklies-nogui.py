#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Download selected comics in getcomics.info weekly packs."""

import sys
import time
from pathlib import Path

from utils.getcomics import get_weekly_comics

my_comics_list = []
config = 'liste-comics.txt'

# Read configfile
try:
    configfile = Path(__file__).parent / config
    with configfile.open("r") as f:
        user_list = f.read().splitlines()
    user_list.sort()

    with configfile.open('w') as f:
        f.writelines([string + '\n' for string in user_list])

    my_comics_list = [comic.lower() for comic in user_list]

except IOError:
    print(f"Erreur : Il faut créer un fichier {config}"
          " et y ajouter vos séries en ligne,\n comme par exemple"
          "\n.........\nBatman\nSuperman\nInjustice\netc...\n.........")
    sys.exit(1)

try:
    get_weekly_comics(my_comics_list)
    time.sleep(5)
except NameError as e:
    print(e)
    print("Le script a rencontré une erreur.\nVous pouvez fermer.")
    time.sleep(5)
