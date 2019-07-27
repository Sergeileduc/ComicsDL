#!/usr/bin/python3
# -*-coding:utf-8 -*-

import requests
from requests.exceptions import HTTPError
# import urllib.request
# from urllib.error import HTTPError

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent': user_agent}


# Find the final url, if redirections occurs
def getfinalurl(url):
    try:
        response = requests.get(url)
        if response.history:
            print("Request was redirected")
            # for resp in response.history:
            #     print(resp.status_code, resp.url)
            # print("Final destination:")
            # print(response.status_code, response.url)
            # print(response.url)
            return response.url
        else:
            # print("Request was not redirected")
            return url
    except HTTPError:
            print("downCom got HTTPError")
            return url
            raise

# Old method for geting final url
# def getfinalurl(url):
#     try:
#         req = urllib.request.Request(url, None, headers)
#         finalurl = urllib.request.urlopen(req).geturl()
#         return finalurl
#     except HTTPError:
#         print("downCom got HTTPError from Request")
#         raise
