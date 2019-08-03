#!/usr/bin/python3
# -*-coding:utf-8 -*-

import os
import subprocess
import copy
from utils import htmlsoup, getcomics

# Constants
from utils.const import DC_URL, MARVEL_URL, IMAGE_URL, INDIE_URL
from utils.const import note, howto, howtodl, consistof
from utils.const import lower, indieweek, bloat


# Find last weekly and display
def printLastWeeklies():
    printLastWeek(DC_URL, "DC")
    printLastWeek(MARVEL_URL, "Marvel")
    printLastWeek(IMAGE_URL, "Image")
    printLastWeek(INDIE_URL, "Indé")


# Def print last weekly date
def printLastWeek(url, editor):
    soup = htmlsoup.url2soup(url)
    lastPost = soup.find_all('article', class_='type-post')[0]
    title = lastPost.h1.a.text
    time = lastPost.find('time')
    print(f'{editor}\t : {title} :\t{time.text}')


# Print getcomics weekly post in file f
def printWeek(url, f, editor):
    global flag
    flag = False
    postTitle, weeklyUrl = getcomics.findLastWeekly2(url)

    # Missing post already been done
    if "Missing" in postTitle and flag:
        pass
    # Missing post not done yet
    elif "Missing" in postTitle and not flag:
        f.write(postTitle + '\n')
        f.write("=====================\n")
        printMultipleEditors(weeklyUrl, f)
        flag = True
    elif editor == "Indé week":
        printMultipleEditors(weeklyUrl, f)
    else:
        printOneEditor(weeklyUrl, f, editor)


# For Marvel, DC, or Image weeklies
def printOneEditor(url, f, editor):
    soup = htmlsoup.url2soup(url)
    var = soup.select_one('section.post-contents > ul').find_all('strong')

    f.write(editor + '\n')
    f.write("=====================\n")
    for s in var:
        s_copy = copy.copy(s)
        for span in s_copy:
            s_copy.span.decompose()
        name = s_copy.text.replace(' : ', '').replace('| ', '')
        a = s.find('a')
        try:
            # if a.has_attr('href'):
            if 'href' in a.attrs:
                f.write(f'[url={a.get("href")}]{name}[/url]\n')
        except Exception:
            f.write(name + '\n')
    f.write("=====================\n")
    f.write("" + '\n')


# For Indie week+
def printMultipleEditors(url, f):
    soup = htmlsoup.url2soup(url).select_one('section.post-contents')

    # List of comics publishers
    publishers = soup.find_all('span', style="color: #3366ff;")
    indies = []
    for p in publishers:
        indies.append(p.text)

    # List of comics
    var = soup.find_all('strong')
    for s in var:
        # Highlight publishers
        if s.text in indies:
            f.write(f'\n{s.text}\n=====================\n')
        # blots
        elif note in s.text \
                or howto in s.text \
                or consistof in s.text \
                or howtodl in s.text \
                or lower in s.text \
                or indieweek in s.text:
            pass
        # more bloats
        elif s.text in bloat:
            pass
        # Comics
        else:
            # make a copy of strong s to remove span
            s_copy = copy.copy(s)
            for span in s_copy:
                s_copy.span.decompose()
            name = s_copy.text.replace(' : ', '').replace('| ', '')
            if s.a and s.a.has_attr('href'):
                f.write(f'[url={s.a.get("href")}]{name}[/url]\n')
            else:
                f.write(f'{name}\n')
    f.write('\n')


# Generate output file
def generateweekly():
    global flag
    flag = False
    try:
        os.remove("liste-comics-semaine.txt")
    except OSError:
        pass

    with open("liste-comics-semaine.txt", "w") as f:
        printWeek(DC_URL, f, "DC week")
        printWeek(MARVEL_URL, f, "Marvel week")
        f.write("Indé week" + '\n')
        f.write("=====================" + '\n')
        printWeek(IMAGE_URL, f, "Image week")
        printWeek(INDIE_URL, f, "Indé week")


# MAIN
print("Les derniers 'weekly packs' de Getcomics sont :")
print("----------------")
printLastWeeklies()
print("----------------")

Join = input('Voulez-vous continuer ? (y/n) ?\n')
if Join.lower() == 'yes' or Join.lower() == 'y':
    print("Processing")
    generateweekly()
    print("Done")
    cmd = 'zenity --text-info --title="Sorties de la semaine"  ' \
          '--width=800 --height=600 --filename=liste-comics-semaine.txt'
    subprocess.call(cmd, shell=True)
else:
    print("Exit")
