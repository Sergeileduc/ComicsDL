#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re
import math

# Subistitions for getcomics
substitutions = {'%2c': '', '%20': ' ', '%28': '(',
                 '%29': ')', '%27': '\'', '%26': '&'}

# Regex to detect name, (year) (tag).extension
regex_tag = r"(.+)(\ \([1|2][9|0]\d{2}\))(.*)(\..{3})"


# Multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


def removetag(filename):
    if re.match(regex_tag, filename):
        # print("match")
        return re.sub(regex_tag, r"\1\2\4", filename)
    else:
        return filename


# Just optimizing
def regexNightmare(html, regex):
    try:
        urlPattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
        return urlPattern.search(str(html)).group(1)
    except Exception as e:
        print(e)
        print("Cant't regex html")


def getZippyDL(url, button):
    print("Found zippyshare : " + url)
    comRawUrl0 = regexNightmare(
        button, r'.*?getElementById.*?href = \"(.*?)\"')
    vara = int(regexNightmare(button, r'.*?var\ a\ =\ (.*?);'))
    varb = int(regexNightmare(button, r'.*?var\ b\ =\ (.*?);'))
    comRawUrl2 = regexNightmare(
        button, r'.*?getElementById.*?href = \".*?\"\+\(.*?\)\+\"(.*?)\"')
    temp = replace(comRawUrl2[1:], substitutions)
    filename = removetag(temp)
    # Calculating the id and forming url
    # that is an extremely dirty way, I know
    try:
        a = int(math.floor(float(vara/3)))
        urlNumFull = a + vara % varb
        fullURL = url[:-21] + comRawUrl0 + str(urlNumFull) + comRawUrl2
        print(fullURL)
    except Exception as e:
        print("Mon erreur")
        print(e)
        raise
    return fullURL, filename
