#!/usr/bin/python3
# -*-coding:utf-8 -*-

import os

from utils import htmlsoup

DCurl = "https://getcomics.info/tag/dc-week/"
MarvelURL = "https://getcomics.info/tag/marvel-now/"
ImageURL = "https://getcomics.info/tag/image-week/"
IndieURL = "https://getcomics.info/tag/indie-week/"

note = "Notes :\n"
howto = "Video guide on how"
howtodl = "how to download"
consistof = "consist of :"
lower = "or on the lower"
bloat = ['Language :', 'Image Format :', 'Year :',
         'Size :', 'Notes :', 'Screenshots :']


# Find las weekly post
def findLastWeekly(url):
    soup = htmlsoup.url2soup(url)
    lastPost = soup.find_all('article', class_='type-post')[0]
    postTitle = lastPost.h1.a.text
    postUrl = lastPost.h1.a['href']
    return postTitle, postUrl


# Find last weekly and display
def printLastWeeklies():
    printLastWeek(DCurl, "DC")
    printLastWeek(MarvelURL, "Marvel")
    printLastWeek(ImageURL, "Image")
    printLastWeek(IndieURL, "Indé")


# Def print last weekly date
def printLastWeek(url, editor):
    soup = htmlsoup.url2soup(url)
    lastPost = soup.find_all('article', class_='type-post')[0]
    title = lastPost.h1.a.text
    time = lastPost.find('time')
    print(editor + '\t : ' + title + ' :\t' + time.text)


# Print getcomics weekly post in file f
def printWeek(url, f, editor):
    global flag
    flag = False
    postTitle, weeklyUrl = findLastWeekly(url)

    # Missing post already been done
    if "Missing" in postTitle and flag:
        pass
    # Missing post not done yet
    elif "Missing" in postTitle and not flag:
        f.write(postTitle + '\n')
        f.write("=====================" + '\n')
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
    f.write("=====================" + '\n')
    for s in var:
        name = s.text.replace(' : ', '').replace('Download', '')\
                    .replace(' | ', '').replace('Read Online', '')
        a = s.find('a')
        try:
            # if a.has_attr('href'):
            if 'href' in a.attrs:
                f.write('[url=' + a.get("href") + ']' + name + '[/url]' + '\n')
        except Exception:
            f.write(name + '\n')
    f.write("=====================" + '\n')
    f.write("" + '\n')


# For Indie week+
def printMultipleEditors(url, f):
    soup = htmlsoup.url2soup(url).select_one('section.post-contents')
    publishers = soup.find_all('span', style="color: #3366ff;")
    indies = []
    for p in publishers:
        indies.append(p.text)

    var = soup.find_all('strong')

    for s in var:
        if s.text in indies:
            f.write('\n' + s.text + '\n=====================' + '\n')
        elif note in s.text \
                or howto in s.text \
                or consistof in s.text \
                or howtodl in s.text \
                or lower in s.text:
            pass
        elif s.text in bloat:
            pass
        else:
            name = s.text.replace(' : ', '').replace('Download', '')\
                        .replace(' | ', '').replace('Read Online', '')
            if s.a and s.a.has_attr('href'):
                f.write(
                    '[url=' + s.a.get("href") + ']' + name + '[/url]' + '\n')
            else:
                f.write(name + '\n')
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
        printWeek(DCurl, f, "DC week")
        printWeek(MarvelURL, f, "Marvel week")
        f.write("Indé week" + '\n')
        f.write("=====================" + '\n')
        printWeek(ImageURL, f, "Image week")
        printWeek(IndieURL, f, "Indé week")


# MAIN
print("Les derniers 'weekly packs' de Getcomics sont :")
print("----------------")
printLastWeeklies()
print("----------------")

Join = input('Voulez-vous continuer ? (y/n) ?\n')
if Join.lower() == 'yes' or Join.lower() == 'y':
    print("Processing")
    generateweekly()
else:
    print ("Exit")
