#!/usr/bin/python3
# -*-coding:utf-8 -*-

import requests
import sys
import os
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

DCurl = "https://getcomics.info/tag/dc-week/"
MarvelURL = "https://getcomics.info/tag/marvel-now/"
ImageURL = "https://getcomics.info/tag/image-week/"
IndieURL = "https://getcomics.info/tag/indie-week/"

note = "Notes :\n"
howto = "Video guide on how"
howtodl = "how to download"
consistof = "consist of :"
lower = "or on the lower"
bloat = ['Language :', 'Image Format :', 'Year :', 'Size :', 'Notes :']

#get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent' : "Fiddler"}
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req)
        html = response.read()
        return html
    except urllib.error.HTTPError as e:
        print (e.fp.read())
        raise

#get BS soup from an url
def url2soup(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    except:
        print("Error")
        raise


#get BS soup from html code
def getSoup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

#find last weekly and display
def printLastWeeklies():
    printLastWeek(DCurl, "DC")
    printLastWeek(MarvelURL, "Marvel")
    printLastWeek(ImageURL, "Image")
    printLastWeek(IndieURL, "Indé")

#def print last weekly date
def printLastWeek(url, editor):
    htmlMain = returnHTML(url)
    soup = getSoup(htmlMain)
    lastPost = soup.find_all('article', class_= 'type-post')[0]
    title = lastPost.h1.a.text
    time = lastPost.find('time')
    print(editor + '\t : ' + title + ' :\t' + time.text)


#find las weekly post
def findLastWeekly(url):
    htmlMain = returnHTML(url)
    soup = getSoup(htmlMain)
    lastPost = soup.find_all('article', class_= 'type-post')[0]
    postTitle = lastPost.h1.a.text
    postUrl = lastPost.h1.a['href']
    return postTitle, postUrl


#print getcomics weekly post in file f
def printWeek(url, f, editor):
    global flag
    flag = False
    postTitle, weeklyUrl = findLastWeekly(url)

    #Missing post already been done
    if "Missing" in postTitle and flag:
        pass
    #Missing post not done yet
    elif "Missing" in postTitle and not flag:
        f.write(postTitle + '\n')
        f.write("=====================" + '\n')
        printMultipleEditors(weeklyUrl, f)
        flag = True
    elif editor == "Indé week":
        printMultipleEditors(weeklyUrl, f)
    else:
        printOneEditor(weeklyUrl, f, editor)

#for Marvel, DC, or Image weeklies
def printOneEditor(url, f, editor):
    soup = url2soup(url)
    #temp = soup.select('section.post-contents > ul > li')
    temp = soup.select('section.post-contents > ul')
    soup2=BeautifulSoup(str(temp), 'html.parser')
    var = soup2.find_all('strong')

    f.write(editor + '\n')
    f.write("=====================" + '\n')
    for s in var:
        name = s.text.replace(' : ','').replace('Download','')\
                    .replace(' | ','').replace('Read Online','')
        a = s.find('a')
        try:
            if 'href' in a.attrs:
            #if a.has_attr('href'):
                f.write('[url=' + a.get("href") + ']' + name  + '[/url]' + '\n')
        except:
            f.write(name + '\n')
    f.write("=====================" + '\n')
    f.write("" + '\n')


#for Indie week+
def printMultipleEditors(url, f):
    soup=url2soup(url).select('section.post-contents')
    soup2=BeautifulSoup(str(soup), 'html.parser')

    publishers = soup2.find_all('span', style="color: #3366ff;")
    indies = []
    for p in publishers:
        indies.append(p.text)

    var = soup2.find_all('strong')

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
            name = s.text.replace(' : ','').replace('Download','')\
                        .replace(' | ','').replace('Read Online','')
            if s.a and s.a.has_attr('href'):
                f.write('[url=' + s.a.get("href") + ']' + name  + '[/url]' + '\n')
            else:
                f.write(name + '\n')
    f.write('\n')

#generate output file
def generateweekly():
    global flag
    flag = False
    try:
        os.remove("liste-comics-semaine.txt")
    except OSError:
        pass

    with open("liste-comics-semaine.txt", "w")  as f:
        printWeek(DCurl, f, "DC week")
        printWeek(MarvelURL, f, "Marvel week")
        f.write("Indé week" + '\n')
        f.write("=====================" + '\n')
        printWeek(ImageURL, f, "Image week")
        printWeek(IndieURL, f, "Indé week")


#MAIN
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
