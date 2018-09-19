#!/usr/bin/python3
# -*-coding:Utf-8 -

import requests
import sys
import os
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

DCurl = "https://getcomics.info/tag/dc-week/"
MarvelURL = "https://getcomics.info/tag/marvel-now/"
IndieURL = "https://getcomics.info/tag/indie-week/"

indies = ['2000AD:', 'ABSTRACT STUDIOS:', 'ACTION LAB:',
'AFTERSHOCK COMICS', 'AFTERSHOCK COMICS:', 'ALBATROSS FUNNYBOOKS:',
'AMERICAN MYTHOLOGY PRODUCTIONS:', 'ANTARTIC PRESS:', 'ANTARCTIC PRESS:',
'ARCHIE COMIC PUBLICATIONS:', 'ASPEN:', 'ASPEN COMICS:', 'AVATAR PRESS:',
'AHOY COMICS:', 'BENITEZ:', 'BLACK MASK COMICS:', 'BOOM! STUDIOS:', 'BOUNDLESS:',
'BROADSWORD COMICS:', 'DANGER ZONE:', 'DARK HORSE COMICS:',
'DYNAMITE ENTERTAINMENT:', 'IDW PUBLISHING:', 'LEGENDARY COMICS:',
'LION FORGE:', 'MAGAZINE:', 'ONI PRESS:', 'RED5:', 'STORM KING PRODUCTIONS:',
'VALIANT:', 'VALIANT ENTERTAINMENT:',
'ZENESCOPE:', 'ZENESCOPE ENTERTAINMENT:']

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


#find las weekly post
def findLastWeekly(url):
    htmlMain = returnHTML(url)
    soup = getSoup(htmlMain)
    lastPost = soup.find_all('article', class_= 'type-post')[0]
    postUrl = lastPost.h1.a['href']
    return postUrl


#print getcomics weekly post
def printWeek(url, f):
    weeklyUrl = findLastWeekly(url)
    soup = url2soup(weeklyUrl)
    temp = soup.select('section.post-contents > ul > li')
    soup2=BeautifulSoup(str(temp), 'html.parser')
    var = soup2.find_all('strong')

    for s in var:
        name = s.text.replace(' : ','').replace('Download','')\
                    .replace(' | ','').replace('Read Online','')
        a = s.find('a')
        try:
            if 'href' in a.attrs:
            #if a.has_attr('href'):
                l = a.get('href')
                f.write('[url=' + a.get("href") + ']' + name  + '[/url]' + '\n')
        except:
            f.write(name + '\n')


#print getcomics Indie+ weekly post
def printIndieWeek(url, f):
    weeklyUrl = findLastWeekly(url)
    soup = url2soup(weeklyUrl)
    temp = soup.select('section.post-contents')
    soup2=BeautifulSoup(str(temp), 'html.parser')
    var = soup2.find_all('strong')
    for s in var:
        if s.text in indies:
            f.write('\n' + s.text + '\n==============================' + '\n')
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
                f.write(s.text + '\n')

#generate output file
def generateweekly():
    try:
        os.remove("liste-comics-semaine.txt")
    except OSError:
        pass

    with open("liste-comics-semaine.txt", "w")  as f:
        f.write("DC week" + '\n')
        f.write("==============================" + '\n')
        printWeek(DCurl, f)
        f.write("==============================" + '\n')
        f.write("" + '\n')
        f.write("Marvel week" + '\n')
        f.write("==============================" + '\n')
        printWeek(MarvelURL, f)
        f.write("==============================" + '\n')
        f.write("" + '\n')
        f.write("Indé week" + '\n')
        f.write("==============================" + '\n')
        printIndieWeek(IndieURL, f)


#MAIN
print("Processing")
generateweekly()
