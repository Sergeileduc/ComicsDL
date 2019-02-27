#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re
import math

#subistitions for getcomics
substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '',
' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'', ' (Webrip-DCP)':'',
' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '',
' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '',
' (Minutemen-Thoth)':'', ' (Glorith-HD)':'', ' (Oroboros-DCP)':'',
'(Digital)(TLK-EMPIRE-HD)':'', ' (Son of Ultron-Empire)':'',
' (Digital-Empire)':'', ' (2 covers)':'', ' GetComics.INFO':'', ' (Mephisto-Empire)':'',
' (Shadowcat-Empire)':''}

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

#just optimizing
def regexNightmare(html, regex):
    try:
        urlPattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
        return urlPattern.search(str(html)).group(1)
    except Exception as e:
        print(e)
        print("Cant't regex html")

def getZippyDL(url, button):
    print("Found zippyshare : " + url)
    comRawUrl0 = regexNightmare(button, r'.*?getElementById.*?href = \"(.*?)\"')
    vara = int(regexNightmare(button, r'.*?var\ a\ =\ (.*?);'))
    varb = int(regexNightmare(button, r'.*?var\ b\ =\ (.*?);'))
    comRawUrl2 = regexNightmare(button, r'.*?getElementById.*?href = \".*?\"\+\(.*?\)\+\"(.*?)\"')
    temp = replace(comRawUrl2[1:], substitutions1)
    filename = replace(temp, substitutions2)
    #calculating the id and forming url | that is an extremely dirty way, I know
    try:
        a = int(math.floor(float(vara/3)))
        urlNumFull = a + vara%varb
        fullURL = url[:-21] + comRawUrl0 + str(urlNumFull) + comRawUrl2
        print(fullURL)
    except Exception as e:
        print("Mon erreur")
        print(e)
        raise
    return fullURL, filename
