#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to parse getcomics.info."""

import re
from datetime import datetime
from time import sleep
from typing import NamedTuple

import requests
from requests.exceptions import HTTPError
from tqdm import tqdm

from utils.htmlsoup import url2soup
from utils.tools import bytes_2_human_readable, NamedUrl, remove_tag
from utils.urltools import getfinalurl
from urllib.parse import quote_plus, unquote

today = datetime.now().strftime("%Y-%m-%d")

basesearch = 'https://getcomics.info'
tagsearch = 'https://getcomics.info/tag/'

getcomicsurls = ['https://getcomics.info/tag/dc-week/',
                 #  'http://getcomics.info/tag/marvel-now/',
                 #  'https://getcomics.info/tag/indie-week/',
                 #  'https://getcomics.info/tag/image-week/'
                 ]

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'  # noqa: E501


class PostInfos(NamedTuple):
    """Store informations on a post, with url, title, and size.
    """
    url: str
    title: str
    size: str = None


def get_weekly_comics(my_list: list) -> None:
    """Compare remote and local list of comics and download."""
    print('Initialisation...')
    print('Je vais chercher les mots clés :')
    print(my_list)

    for url in getcomicsurls:
        # Other soup selectors
        # select_one("section.post-contents > ul")\
        # find_all('span', style="color: #ff0000;")
        remote_comics_list = comics_list(url)
        # print(f"{remote_comics_list = }")
        for newcomic in remote_comics_list:
            try:
                for my_comics in my_list:
                    if my_comics in newcomic.name:
                        download_comic(newcomic.url)
            except Exception as e:
                print(f"Error in 'get_weekly_comics : {e}")
    print("C'est tout. Vous pouvez fermer.")


def find_last_weekly(url) -> NamedUrl:
    """Find las weekly post.

    Args:
        url (str): url of all weekly posts

    Returns:
        NamedUrl: Title and url of last weekly post
    """
    last_post = url2soup(url).find('article', class_='type-post')
    # Check if today's archive is there, and retrieve its url
    # print(f"Latest weekly post: {lastPost.time['datetime']}")
    # TODO : code for auotmate, maybe uncode later
    # if today in lastPost.time['datetime']:
    #     # print ('There is a new one today. Hurrah!')
    #     pass
    # else:
    #     # print ('Nothing yet. Exiting...')
    #     # print ('Continue anyway...')
    #     # quit()
    #     pass
    # post_title = last_post.h1.a.text
    # post_url = last_post.h1.a['href']
    # return post_title, post_url
    return NamedUrl(name=last_post.h1.a.text,
                    url=last_post.h1.a['href'])


def comics_list(url: str) -> list[NamedUrl]:
    """Get list of Name/URL for comics posts in the weekly pack.

    Args:
        url (str): url of getcomics weeklies page.

    Returns:
        list[NamedUrl]: liste of all comics (NamedUrl with name and url keys)
    """
    weekly_url = find_last_weekly(url).url
    content = url2soup(weekly_url).select_one("section.post-contents")
    posts_links = content.select("ul > li > strong")

    res_list: list(NamedUrl) = []
    for post in posts_links:
        try:
            name: str = post.contents[0].lower()  # Text on the post link
            a = post.select_one('span > a')
            if a.has_attr('href') and a.text == "Download":
                url: str = a.get('href')
            res_list.append(NamedUrl(name=name, url=url))
        except TypeError:
            pass
        except Exception as e:
            print(f"comics_list Error : {e}")
    return res_list


def getresults(url: str) -> list[PostInfos]:
    """Search Getcomics.

    Returns names and urls of posts returned by input url.

    Args:
        url (str): getcomics search url.

    Returns:
        list: list of posts in format dict : {"url": url, "title": title, "size": size}
    """
    searchlist: list[PostInfos] = []
    try:
        res = url2soup(url).select("div.post-info")
        for d in res:
            if d.h1.a.has_attr('href'):
                size = None
                if searchsize := re.search(r'\d+ [KMGT]B', d.p.text, re.MULTILINE | re.IGNORECASE):
                    size: str = searchsize[0]
                result = PostInfos(url=d.h1.a.get("href"),
                                   title=d.h1.a.text,
                                   size=size)
                searchlist.append(result)
    except HTTPError as e:
        print(e)
        print("something wrong happened")
    return searchlist


def _find_dl_buttons(url):
    """Find download buttons in a getcomics pages."""
    return url2soup(url).select("div.aio-pulse > a")


def download_comic(url: str) -> None:
    """Find Zippyshare Button, find download url, download.

    Args:
        url (str): getcomics "post" url for a comicbook
    """
    final_url: str = getfinalurl(url)  # handle possible redirecteions
    print(f"download_comic function with : {final_url}")
    try:
        direct_url, name, size = getcomics_directlink(final_url)
    except DLurlError as e:
        print(f"download_comic got Error : {e}")
    except HTTPError as e:
        print(f"download_comic got Error : {e}")
        raise
    try:
        print(f"{direct_url = }")
        _write_comics(direct_url, name, size)
    except Exception as e:
        print("error in write comics")
        print(f"download_comic got Error : {e}")


def _write_comics(url: str, name: str, size: int) -> None:
    try:
        r: requests.Response = requests.get(url, stream=True)
        print(f"size = {bytes_2_human_readable(size)}")
    except Exception as e:
        print("Can't get download link")
        print(f"_write_comics error {e}")

    # Download from url & trim it a little bit
    with open(remove_tag(name), 'wb') as f:
        try:
            for block in tqdm(iterable=r.iter_content(1024), total=size / 1024):
                f.write(block)
        except KeyboardInterrupt:
            pass
        except IOError as e:
            print(f"_write_comics : Error while writing file : {e}")
    r.close()
    print('Done\n--')


def searchurl(user_search: str, mode: int, page: int) -> str:
    """Return a getcomics research URL.

    Args:
        user_search (str): input user search (example: 'Iron Man')
        mode (int): search mode (classic: 1 or by tag: 0)
        page (int): index of the page

    Returns:
        str: url for getting search results.
    """

    # Research with tag (https://getcomics.info/tag/......)
    if mode == 0:
        # Page 1 (no page number on this one)
        return (
            f"{tagsearch}{user_search.lower().replace(' ', '-')}"
            if page == 1
            else f"{tagsearch}{user_search.lower().replace(' ', '-')}/page/{page}/"
        )

    # Classic research https://getcomics.info/?s=
    elif page == 1:
        return f"{basesearch}/?s={quote_plus(user_search.lower())}"
    # else
    return f"{basesearch}/page/{page}/?s={quote_plus(user_search.lower())}"


def getcomics_directlink(comic_url: str):
    """Get download links in a getcomics post."""
    # BeautifulSoup will transform raw HTML in a tree easy to parse
    soup = url2soup(comic_url)
    direct_download = soup.find('a', class_='aio-red')

    # temp_url is not the final cbz or cbr download url
    temp_url = direct_download.get('href')

    # We follow temp_url to find final URL
    sleep(1)

    with requests.Session() as session:
        r = session.get(temp_url, allow_redirects=False, timeout=3)  # noqa:E501

    if r.status_code == 200:
        size: int = int(r.headers['Content-length'])
        name: str = unquote(r.url.split("/")[-1])
        return r.url, name, size
    elif r.status == 302:
        return r.headers['location']
    else:
        raise DLurlError


def find_buttons(url: str) -> list:
    """Find download buttons in html soup, return list of buttons."""
    return url2soup(url).select("div.aio-pulse > a")


class DLurlError(Exception):
    "raised when program cannot find the dl url"
    pass
