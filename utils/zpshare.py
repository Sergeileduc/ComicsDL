#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to download on zippyshare."""

import asyncio
import base64
import re
from urllib.parse import unquote, urlparse

import pyppeteer
import requests
from requests_html import AsyncHTMLSession
from requests.exceptions import HTTPError

from utils.htmlsoup import url2soup
# from urllib.error import HTTPError

from utils.tools import search_regex_name

BASE = "https://getcomics.info/go.php-url=/"

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}  # noqa:E501


# Regex to detect name, (year) (tag).extension
regex_tag = r"(.+)(\ \([1|2][9|0]\d{2}\))(.*)(\..{3})"
#  Regex for finding the name of the file
regex_rawname = r"/d/.*./*.?/(?P<name>.*)"


def _remove_tag(filename):
    if re.match(regex_tag, filename):
        # print("match")
        return re.sub(regex_tag, r"\1\2\4", filename)
    else:
        return filename


def get_file_filename_url(url: str) -> tuple[str, str]:
    """Find filename and download url in a zippyshare page.

    Args:
        url (str): zippyshare page url

    Returns:
        tuple[str, str]: full download URL, filename
    """
    print("Found zippyshare : " + url)
    # session = HTMLSession()
    # print("HTML session created")
    # r = session.get(url, headers=headers)
    # session.close()
    # print("HTML session closed")
    # r.html.render()
    # print("r.html.render() is OK")
    html = asyncio.run(async_render(url))
    button = html.find("a#dlbutton", first=True)
    partial_url = button.attrs["href"]
    raw_name = search_regex_name(partial_url, regex_rawname, 'name')
    file_name = _remove_tag(unquote(raw_name).strip('/'))
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    full_url = f"{domain}{partial_url}"
    print(f"{full_url = }")
    return full_url, file_name


async def async_render(url: str):
    asession = AsyncHTMLSession()
    browser = await pyppeteer.launch({
        'ignoreHTTPSErrors': True,
        'headless': True,
        'handleSIGINT': False,
        'handleSIGTERM': False,
        'handleSIGHUP': False
    })
    asession._browser = browser
    r = await asession.get(url, headers=headers)
    await r.html.arender()
    await asession.close()
    return r.html


def check_url(zippylink: str) -> str:
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
