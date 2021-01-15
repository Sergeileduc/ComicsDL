#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to download on zippyshare."""

import re
import requests
from requests.exceptions import HTTPError
import base64
from urllib.parse import unquote, urlparse
# from urllib.error import HTTPError
# perso
from utils.tools import search_regex_name
from utils.htmlsoup import url2soup

BASE = "https://getcomics.info/go.php-url=/"

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

# Regex to detect name, (year) (tag).extension
regex_tag = r"(.+)(\ \([1|2][9|0]\d{2}\))(.*)(\..{3})"

regex_first = r'.*?getElementById.*?href ?= ?\"(?P<first>.*?)\"'

regex_abcd = r'.*?getElementById.*?href = \"(.*?)\" \+ \((?P<a>\d+) \% (?P<b>\d+) \+ (?P<c>\d+) \% (?P<d>\d+)\)'  # noqa: E501

# regex_rawname = (r'.*?getElementById.*?href = '
#                  r'\".*?\" \+ \(.*?\) \+ \"(?P<name>.*?)\"')
# regex_rawname = r".*?getElementById.*?href = \".*?\"\+\(.*\)\+\"/(?P<name>.*?)\""  # noqa: E501
regex_rawname = r'.*?getElementById.*?href ?= ?\".*?\" ?\+ ?\(.*\) ?\+ ?\"\/?(?P<name>.*?)\"'  # noqa: E501

regex_vara = r"var a = (?P<A>\d+)"


def _remove_tag(filename):
    if re.match(regex_tag, filename):
        # print("match")
        return re.sub(regex_tag, r"\1\2\4", filename)
    else:
        return filename


def get_file_url(url, button):
    """Find filename and download url."""
    print("Found zippyshare : " + url)
    first_part = search_regex_name(button, regex_first, 'first')
    print(first_part)
    a = int(search_regex_name(button, regex_abcd, 'a'))
    # a = int(search_regex_name(button, regex_vara, 'A'))
    b = int(search_regex_name(button, regex_abcd, 'b'))
    # b = 3
    c = int(search_regex_name(button, regex_abcd, 'c'))
    d = int(search_regex_name(button, regex_abcd, 'd'))

    raw_name = search_regex_name(button, regex_rawname, 'name')
    # unquote replace special characters like %2c, etc..
    filename = _remove_tag(unquote(raw_name).strip('/'))
    # Calculating the id and forming url
    # that is an extremely dirty way, I know
    second_part = a % b + c % d
    # second_part = a**3+b

    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    full_url = f"{domain}{first_part}{second_part}/{raw_name}"
    print(full_url)
    return full_url, filename


def check_url(zippylink):
    """Check url."""
    try:
        # TODO : verify if useful
        if str(zippylink).startswith(BASE):
            finalzippy = base64.b64decode(zippylink[len(BASE):]).decode()
        else:
            finalzippy = requests.get(zippylink).url
        return finalzippy
    except HTTPError as e:
        print("can't obtain final zippyshare url")
        print(e)
        raise


def find_zippy_download_button(zippy_url):
    """Find download button on zippyshare page."""
    try:
        soup = url2soup(zippy_url)
        return soup.find('a', id="dlbutton").find_next_sibling()
    except Exception:
        raise DownloadButtonError("Error on zp page : "
                                  "No download button found")


class DownloadButtonError(Exception):
    """Error."""

    def __init__(self, msg):
        """Init with msg."""
        super().__init__(self, msg)
