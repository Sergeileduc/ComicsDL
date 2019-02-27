#!/usr/bin/python3
# -*-coding:utf-8 -*-
import os
import getcomics
import time
import htmlsoup

getcomicsurls = ['https://getcomics.info/tag/dc-week/',
                'http://getcomics.info/tag/marvel-now/',
                'https://getcomics.info/tag/indie-week/',
                'https://getcomics.info/tag/image-week/'
                ]

myComicsList = list()
#myComicsList = ['batman', 'superman', 'fathom, 'deadpool]

config = 'liste-comics.txt'

#read configfile
try:
    configfile = os.path.join(os.path.dirname(__file__), config)
    userList = list()
    with open(configfile, 'r+') as f:
        userList = f.read().splitlines()
        userList.sort()
    with open(configfile, 'w+') as f:
        for comic in userList:
            f.write('%s\n' % comic)
            myComicsList.append(comic.lower().replace(' ','-'))
except IOError as e:
    print("Erreur : Il faut créer un fichier " + config + " et y ajouter vos séries en ligne,\n comme par exemple\n.........\nBatman\nSuperman\nInjustice\netc...\n.........")

try:
    print("Je vais chercher : " + str(myComicsList))

    #get list of all comics from the last "Weekly" pack
    for url in getcomicsurls:
        remoteComicsList = getcomics.comicsList(url)
        for newcomic in remoteComicsList:
            try:
                for myComic in myComicsList:
                    if myComic in newcomic:
                        getcomics.downCom(newcomic)
                        pass
            except Exception as e:
                print(e)
                pass
    print("C'est tout. Vous pouvez fermer.")
    time.sleep(20)
except NameError:
    print("Le script a rencontré une erreur.\nVous pouvez fermer.")
    time.sleep(20)
