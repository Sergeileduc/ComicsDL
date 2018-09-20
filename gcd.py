#!/usr/bin/python3
# -*-coding:utf-8 -*-
import re
import requests
import os
import time
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from datetime import datetime

getcomicsurl = "https://getcomics.info/tag/dc-week/"
#getcomicsurl = "http://getcomics.info/tag/marvel-now/"
#getcomicsurl = "https://getcomics.info/tag/indie-week/"
myComicsList = list()
#myComicsList = ['batman', 'superman']
#myComicsList = ['deadpool', 'captain-america', 'x-men-gold']
#myComicsList = ['fathom', 'dark-ark']

config = 'liste-dc.txt'
#config = 'liste-marvel.txt'
#config = 'liste-indie.txt'

substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '',
' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'',
' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '',
' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '',
' (Minutemen-Thoth)':'', ' (Glorith-HD)':'', ' (Oroboros-DCP)':'',
'(Digital)(TLK-EMPIRE-HD)':'', ' (Son of Ultron-Empire)':'',
' (Digital-Empire)':'', ' (2 covers)':'', ' GetComics.INFO':''}

today = datetime.today().strftime("%Y-%m-%d")

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

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

#get beautiful soup
def getSoup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

#get inner html from tag
def getTagClassData(html, tag, classname):
    soup = getSoup(html)
    list = soup.find_all(tag, class_=classname)
    return list

#get inner html from tag
def getTagData(html, tag, attr, name):
    soup = getSoup(html)
    list = soup.find_all(tag, {attr: name})
    return list

def getaALLhref(html, tag):
    urllist = list()
    soup = getSoup(html)
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist

#find las weekly post
def findLastWeekly(htmlMain):
    lastPost = getTagClassData(htmlMain, 'article', 'type-post')[0]
    #check if today's archive is there, and retrieve its url
    print ("Latest weekly post: " + lastPost.time['datetime'])
    if today in lastPost.time['datetime']:
        #print ('There is a new one today. Hurrah!')
        pass
    else:
        #print ('Nothing yet. Exiting...')
        #print ('Continue anyway...')
        #quit()
        pass
    postUrl = lastPost.h1.a['href']
    return postUrl

#find download link
def downCom(url):
    print ("Found " + url)
    zippylink = ''
    try:
        html = returnHTML(url)
        downButtons = getTagClassData(html, 'div', 'aio-pulse')
        for button in downButtons:
            if 'zippyshare' in str(button).lower() and 'href' in button.a.attrs:
                #downComZippy(button.a['href'])
                zippylink = button.a['href']
                downComZippy(zippylink)
    except urllib.error.HTTPError:
        print("downCom got HTTPError from returnHTML")
        raise
    return

#just optimizing
def regexNightmare(html, regex):
    try:
        urlPattern = re.compile(regex, re.I)
        return urlPattern.search(str(html)).group(1)
    except:
        print("Cant't regex html")

def getZippyDL(url, button):
    print("Found zippyshare : " + url)

    #disassemble url
    comRawUrl0 = regexNightmare(button, r'.*?getElementById.*?href = \"(.*?)\"')
    comRawUrl1 = regexNightmare(button, r'.*?getElementById.*?href = \".*?\" \+ \((.*?)\) \+ \".*?\"\;')
    comRawUrl2 = regexNightmare(button, r'.*?getElementById.*?href = \".*?\" \+ .*? \+ \"(.*?)\"\;')
    #filename = comRawUrl2[1:].replace('%20',' ').replace('%28','(').replace('%29',')').replace('%2c','')
    temp = replace(comRawUrl2[1:], substitutions1)
    filename = replace(temp, substitutions2)
    #calculating the id and forming url | that is an extremely dirty way, I know
    try:
        urlPattern = re.compile(r'(.*?) \% (.*?) \+ (.*?) \% (.*?)$', re.I)
        urlNum1 = urlPattern.search(str(comRawUrl1)).group(2)
        urlNum2 = urlPattern.search(str(comRawUrl1)).group(3)
        urlNum3 = urlPattern.search(str(comRawUrl1)).group(4)
        urlNumFull = (int(urlNum2) % int(urlNum1)) + (int(urlNum2) % int(urlNum3))
        fullURL = url[:-21] + comRawUrl0 + str(urlNumFull) + comRawUrl2
    except Exception as e:
        print("Mon erreur")
        print(e)
        raise
    return fullURL, filename

#download from zippyshare
def downComZippy(url):
    zippyHTML = returnHTML(url)
    #downButton = getTagClassData(zippyHTML, 'div', 'right')
    downButton = getTagData(zippyHTML, "script", "type", "text/javascript")
    try:
        fullURL, fileName = getZippyDL(url, downButton)
        print ("Downloading from " + fullURL + "\ninto : " + fileName)
        r = requests.get(fullURL)
    except:
        print("Can't get download link on zippyshare page")

    #download from url & trim it a little bit
    with open(fileName, 'wb') as f:
        try:
            for block in r.iter_content(1024):
                f.write(block)
        except KeyboardInterrupt:
            pass
        except IOError:
            print("Error while writing file")
    print ('Done\n--')
    return

#get latest archive on the current page
htmlMain = returnHTML(getcomicsurl)
weeklyUrl = findLastWeekly(htmlMain)
interm = getTagClassData(returnHTML(weeklyUrl), 'section', 'post-contents')
interm2 = getTagClassData(str(interm), 'li', '')
comList = getaALLhref(str(interm2), 'a')

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
    print("Erreur : Il faut créer un fichier " + config + " dans le dossier du script et y ajouter vos séries en ligne,\n comme par exemple\n.........\nBatman\nSuperman\nInjustice\netc...\n.........")

try:
    print("Je vais chercher : " + str(myComicsList))
    for newcomic in comList:
        try:
            for myComic in myComicsList:
                if myComic in newcomic:
                    downCom(newcomic)
                    pass
        except Exception as e:
            print(e)
            pass
    print("C'est tout. Vous pouvez fermer.")
    time.sleep(20)
except NameError:
    print("Le script a rencontré une erreur.\nVous pouvez fermer.")
    time.sleep(20)
