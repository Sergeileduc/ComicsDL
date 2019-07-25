#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re
import requests
import base64
from urllib.parse import unquote
from urllib.error import HTTPError
# perso
from utils.tools import searchRegexName
from utils.htmlsoup import url2soup

BASE = "https://getcomics.info/go.php-url=/"

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

# Regex to detect name, (year) (tag).extension
regex_tag = r"(.+)(\ \([1|2][9|0]\d{2}\))(.*)(\..{3})"

regex_first = r'.*?getElementById.*?href = \"(?P<first>.*?)\"'

regex_abcd = (r'.*?getElementById.*?href = \"(.*?)\"'
              r' \+ \((?P<a>\d+) \% (?P<b>\d+) \+ (?P<c>\d+) \% (?P<d>\d+)\)')

regex_rawname = (r'.*?getElementById.*?href = '
                 r'\".*?\" \+ \(.*?\) \+ \"(?P<name>.*?)\"')


def _removetag(filename):
    if re.match(regex_tag, filename):
        # print("match")
        return re.sub(regex_tag, r"\1\2\4", filename)
    else:
        return filename


def getFileUrl(url, button):
    print("Found zippyshare : " + url)
    first_part = searchRegexName(button, regex_first, 'first')
    a = int(searchRegexName(button, regex_abcd, 'a'))
    b = int(searchRegexName(button, regex_abcd, 'b'))
    c = int(searchRegexName(button, regex_abcd, 'c'))
    d = int(searchRegexName(button, regex_abcd, 'd'))

    raw_name = searchRegexName(button, regex_rawname, 'name')
    # unquote replace special characters like %2c, etc..
    filename = _removetag(unquote(raw_name).strip('/'))
    # Calculating the id and forming url
    # that is an extremely dirty way, I know
    second_part = a % b + c % d
    fullURL = url[:-21] + first_part + str(second_part) + raw_name
    print(fullURL)
    return fullURL, filename


def checkurl(zippylink):
    try:
        # TODO : verify if usefull
        if str(zippylink).startswith(BASE):
            print("Abracadabra !")
            finalzippy = base64.b64decode(zippylink[len(BASE):]).decode()
        else:
            finalzippy = requests.get(zippylink).url
        return finalzippy
    except HTTPError as e:
        print("can't obtain final zippyshare url")
        print(e)
        raise


# TODO : maybe underscore for internal use only
def find_zippy_download_button(zippyurl):
    try:
        soup = url2soup(zippyurl)
        # downButton = soup.select('script[type="text/javascript"]')
        return soup.find('a', id="dlbutton").find_next_sibling().text
    except Exception:
        raise DownloadButtonError("Error on zp page : "
                                  "No download button found")


class DownloadButtonError(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)
