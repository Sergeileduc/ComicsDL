#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re #regex
import requests #html
import urllib.request
import urllib.error
from datetime import datetime
from bs4 import BeautifulSoup
import htmlsoup
import zpshare
import base64
import tools

today = datetime.today().strftime("%Y-%m-%d")

basesearch = 'https://getcomics.info'
tagsearch = 'https://getcomics.info/tag/'

getcomicsurls = ['https://getcomics.info/tag/dc-week/',
                'http://getcomics.info/tag/marvel-now/',
                'https://getcomics.info/tag/indie-week/',
                'https://getcomics.info/tag/image-week/'
                ]

BASE = "https://getcomics.info/go.php-url=/"

#find las weekly post
def findLastWeekly(url):
    soup = htmlsoup.url2soup(url)
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

def comicsList(url):
    weeklyUrl = findLastWeekly(url)
    soup = htmlsoup.url2soup(weeklyUrl)
    interm = soup.select("section.post-contents")
    soup2 = BeautifulSoup(str(interm), 'html.parser')
    interm2 = soup2.find_all('li')
    return htmlsoup.getaALLhref(str(interm2), 'a')

#find download link
def downCom(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    try:
        req = urllib.request.Request(url, None, headers)
        finalurl = urllib.request.urlopen(req).geturl()
    except urllib.error.HTTPError:
        print("downCom can't get final url")
        raise
    print ("Trying " + finalurl)
    zippylink = ''
    try:
        soup = htmlsoup.url2soup(finalurl)
        downButtons = soup.select("div.aio-pulse > a")
    except:
        print("Here is the Error")
    for button in downButtons:
        #if 'zippyshare' in str(button).lower() and 'href' in button.a.attrs:
        if 'zippyshare' in button.get("href") or 'zippyshare' in button.get('title').lower():
            zippylink = button.get("href")
            print(zippylink)
            try:
                if str(zippylink).startswith(BASE):
                    print("Abracadabra !")
                    finalzippy = base64.b64decode(zippylink[len(BASE):]).decode()
                else:
                    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
                    headers = { 'User-Agent' : user_agent }
                    req = urllib.request.Request(zippylink, None, headers)
                    finalzippy = urllib.request.urlopen(req).geturl()
            except urllib.error.HTTPError as e:
                print("can't obtain final zippyshare page url")
                print(e)
                raise
            except IOError:
                print("Zippyhare download failed")
            try:
                print(finalzippy)
                downComZippy(finalzippy)
            except:
                print("error in downComZippy")
    return

#download from zippyshare
def downComZippy(url):
    soup = htmlsoup.url2soup(url)
    #downButton = soup.select('script[type="text/javascript"]')
    downButton = soup.find('a', id="dlbutton").find_next_sibling().text
    try:
        fullURL, fileName = zpshare.getZippyDL(url, downButton)
        print ("Downloading from zippyshare into : " + fileName)
        r = requests.get(fullURL, stream=True)
        size = tools.bytes_2_human_readable(int(r.headers['Content-length']))
        print(size)
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
    r.close()
    print ('Done\n--')
    return

def getWeeklyComics(mylist):
    print ('Initialisation...')
    print ('Je vais chercher les mots clés :')
    print (mylist)

    for url in getcomicsurls:
    #get latest archive on the current page
        weeklyUrl = findLastWeekly(url)
        soup = htmlsoup.url2soup(weeklyUrl)
        interm = soup.select("section.post-contents")
        soup2 = BeautifulSoup(str(interm), 'html.parser')
        interm2 = soup2.find_all('li')
        remoteComicsList = htmlsoup.getaALLhref(str(interm2), 'a')
        for newcomic in remoteComicsList:
            try:
                for myComic in mylist:
                    if myComic in newcomic:
                        downCom(newcomic)
                        pass
            except Exception as e:
                print(e)
                pass
    print("C'est tout. Vous pouvez fermer.")

#search Getcomics
def getresults(url):
    searchlist=list()
    try:
        soup = htmlsoup.url2soup(url)
        for d in soup.select("div.post-info"):
            if d.h1.a.has_attr('href'):
                size = None
                searchsize = re.search( r'\d+ [KMGT]B', d.p.text, re.M|re.I)
                if searchsize:
                    size = searchsize.group(0)
                searchlist.append((d.h1.a.get("href"),d.h1.a.text, size))
        #print(searchlist)
        return searchlist
    except urllib.error.HTTPError:
        print("something wrong happened")

#returns a getcomics research URL
def searchurl(user_search, mode, page):
    #research with tag (https://getcomics.info/tag/......)
    if mode == 0:
        #page 1 (no page number on this one)
        if page == 1:
            url = tagsearch + user_search.lower().replace(' ', '-')
        #other pages
        else:
            url = tagsearch + user_search.lower().replace(' ', '-') + '/page/' + str(page) + '/'
    #classic research https://getcomics.info/?s=
    else:
        #page 1
        if page == 1:
            url = basesearch + '/?s=' + user_search.lower().replace(' ', '+')
        #other pages
        else:
            url = basesearch + '/page/' + str(page) + '/?s=' + user_search.lower().replace(' ', '+')
    return url
