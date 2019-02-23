#!/usr/bin/python3
# -*-coding:utf-8 -*-
import os
import re
import requests
import time
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from datetime import datetime

#getcomicsurl = "https://getcomics.info/tag/dc-week/"
getcomicsurl = "http://getcomics.info/tag/marvel-now/"
#getcomicsurl = "https://getcomics.info/tag/indie-week/"
myComicsList = list()
#myComicsList = ['batman', 'superman']
#myComicsList = ['deadpool', 'captain-america', 'x-men-gold']
#myComicsList = ['fathom', 'dark-ark']

#config = 'liste-dc.txt'
config = 'liste-marvel.txt'
#config = 'liste-indie.txt'

substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '',
' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'',
' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '',
' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '',
' (Minutemen-Thoth)':'', ' (Glorith-HD)':'', ' (Oroboros-DCP)':'',
'(Digital)(TLK-EMPIRE-HD)':'', ' (Son of Ultron-Empire)':''}

today = datetime.today().strftime("%Y-%m-%d")

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

# get html from url
def returnHTML(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    #hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    try:
        req = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        response.close()
        return html
    except ValueError as e:
        print(e)
        raise
    except urllib.error.HTTPError as e:
        print(e)
        raise

#def url 2 soup
def url2soup(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    except:
        print("Error in URL -> soup")
        raise

#get beautiful soup
def html2soup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def getaALLhref(html, tag):
    urllist = list()
    soup = html2soup(html)
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist

#find las weekly post
def findLastWeekly(url):
    soup = url2soup(url)
    lastPost = soup.find('article', class_='type-post')
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
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    try:
        req = urllib.request.Request(url, None, headers)
        finalurl = urllib.request.urlopen(req).geturl()
    except urllib.error.HTTPError:
        print("downCom got HTTPError from returnHTML")
        raise
    print ("Trying " + finalurl)
    zippylink = ''
    try:
        soup=url2soup(finalurl)
        downButtons = soup.select("div.aio-pulse > a")
        for button in downButtons:
            #if 'zippyshare' in str(button).lower() and 'href' in button.a.attrs:
            if 'zippyshare' in button.get("href") or 'zippyshare' in button.get('title').lower():
                zippylink = button.get("href")
                try:
                    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
                    headers = { 'User-Agent' : user_agent }
                    req = urllib.request.Request(zippylink, None, headers)
                    print(req)
                    finalzippy = urllib.request.urlopen(req).geturl()
                except urllib.error.HTTPError:
                    print("can't obtain final zippyshare url")
                    raise
                except IOError:
                    print("Zippyhare download failed")
                #try:
                print(finalzippy)
                downComZippy(finalzippy)
                #except:
                #    print("error in downComZippy")
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
    print("Zippy")
    soup=url2soup(url)
    downButton = soup.select('script[type="text/javascript"]')
    try:
        fullURL, fileName = getZippyDL(url, downButton)
        print ("Downloading from zippyshare into : " + fileName)
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
weeklyUrl = findLastWeekly(getcomicsurl)
soup = url2soup(weeklyUrl)
interm = soup.select("section.post-contents")
soup2 = BeautifulSoup(str(interm), 'html.parser')
interm2 = soup2.find_all('li')
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
        except Exception as e:
            print(e)
    print("C'est tout. Vous pouvez fermer.")
    time.sleep(20)
except NameError:
    print("Le script a rencontré une erreur.\nVous pouvez fermer.")
    time.sleep(20)
