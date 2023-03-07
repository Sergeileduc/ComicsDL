#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to download on zippyshare."""

import asyncio
import base64
import re
from urllib.parse import unquote

import pyppeteer
import requests
from requests_html import AsyncHTMLSession, HTMLResponse, HTML
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


def _remove_tag(filename: str) -> str:
    """Remove "tags" in the name of the file.
    Like (Teams) (Format) (size) etc...

    Args:
        filename (str): the original filename

    Returns:
        str: the filename without all the tags
    """
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
    print(f"Found zippyshare : {url}")
    html: HTML = asyncio.run(async_render(url, selector='div.right'))
    button = html.find("a#dlbutton", first=True)
    partial_url: str | None = button.attrs.get("href")
    full_url: str = html._make_absolute(partial_url)
    raw_name: str = search_regex_name(partial_url, regex_rawname, 'name')
    file_name: str = _remove_tag(unquote(raw_name).strip('/'))
    print(f"{full_url = }, {file_name = }")
    return full_url, file_name


async def async_render(url: str, selector: str = None, timeout: int = None) -> HTML:
    """Render a webpage (or a portion of a page, using the selector)

    Args:
        url (str): url of the webpage
        selector (str, optional): CSS selector to only render portion of the page.
            Defaults to None.. Defaults to None.
        timeout (int, optional): timeout in seconds. Defaults to None.

    Returns:
        HTML: HTML object ready for parsing.
    """
    asession = AsyncHTMLSession()
    browser = await pyppeteer.launch({
        'ignoreHTTPSErrors': True,
        'headless': True,
        'handleSIGINT': False,
        'handleSIGTERM': False,
        'handleSIGHUP': False
    })
    asession._browser = browser
    r: HTMLResponse = await asession.get(url, headers=headers, timeout=timeout)
    if selector:
        selected = r.html.find(selector, first=True)
        r.html.html = str(selected)  # 1st html is an HTML object, 2nd is str or bytes.
    await r.html.arender()
    await asession.close()
    return r.html


def check_url(zippylink: str) -> str:
    """Check url."""
    try:
        return (
            base64.b64decode(zippylink[len(BASE):]).decode()
            if zippylink.startswith(BASE)
            else requests.get(zippylink).url
        )
    except HTTPError as e:
        print("can't obtain final zippyshare url")
        print(e)
        raise


def find_zippy_download_button(zippy_url: str):
    """Find download button on zippyshare page."""
    try:
        soup = url2soup(zippy_url)
        return soup.find('a', id="dlbutton").find_next_sibling()
    except Exception as e:
        raise DownloadButtonError("Error on zp page : " "No download button found") from e


class DownloadButtonError(Exception):
    """Error."""

    def __init__(self, msg):
        """Init with msg."""
        super().__init__(self, msg)
