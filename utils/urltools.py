#!/usr/bin/python3
# -*-coding:utf-8 -*-

import urllib.request
from urllib.error import HTTPError

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent': user_agent}


def getfinalurl(url):
    try:
        req = urllib.request.Request(url, None, headers)
        finalurl = urllib.request.urlopen(req).geturl()
        return finalurl
    except HTTPError:
        print("downCom got HTTPError from Request")
        raise
