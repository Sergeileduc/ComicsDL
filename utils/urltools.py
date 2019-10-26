#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Some functions with urls."""

import requests
from requests.exceptions import HTTPError

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent': user_agent}


def getfinalurl(url):
    """Follow redirections and get final url."""
    try:
        response = requests.get(url)
        if response.history:
            print("Request was redirected")
            # for resp in response.history:
            #     print(resp.status_code, resp.url)
            return response.url
        else:
            return url
    except HTTPError:
        print("down_com got HTTPError")
        return url
