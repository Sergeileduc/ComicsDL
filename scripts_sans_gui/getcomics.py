#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re #regex
import requests #html
import urllib.request
import urllib.error
from datetime import datetime
from bs4 import BeautifulSoup
import htmlsoup
import base64

today = datetime.today().strftime("%Y-%m-%d")

BASE = "https://getcomics.info/go.php-url=/"

#subistitions for getcomics
substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '',
' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'',
' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '',
' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '',
' (Minutemen-Thoth)':'', ' (Glorith-HD)':'', ' (Oroboros-DCP)':'',
'(Digital)(TLK-EMPIRE-HD)':'', ' (Son of Ultron-Empire)':'',
' (Digital-Empire)':'', ' (2 covers)':'', ' GetComics.INFO':'', ' (Mephisto-Empire)':''}

#just optimizing
def regexNightmare(html, regex):
    try:
        urlPattern = re.compile(regex, re.I)
        return urlPattern.search(str(html)).group(1)
    except:
        print("Cant't regex html")

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

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
            #try:
            print(finalzippy)
            downComZippy(finalzippy)
                #except:
                #    print("error in downComZippy")
    #except urllib.error.HTTPError:
        #print("downCom got HTTPError from returnHTML")
        #raise
    return

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
    soup = htmlsoup.url2soup(url)
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
