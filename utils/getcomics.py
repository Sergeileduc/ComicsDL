#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to parse getcomics.info."""

import re  # regex
import requests  # html
from requests.exceptions import HTTPError
from datetime import datetime
from utils.htmlsoup import url2soup, get_href_with_name
from utils import zpshare
from utils import tools
from utils.urltools import getfinalurl
from urllib.parse import quote_plus
from utils.zpshare import check_url
# from utils.getcomics_exceptions import NoZippyButton

today = datetime.today().strftime("%Y-%m-%d")

basesearch = 'https://getcomics.info'
tagsearch = 'https://getcomics.info/tag/'

getcomicsurls = ['https://getcomics.info/tag/dc-week/',
                 #  'http://getcomics.info/tag/marvel-now/',
                 #  'https://getcomics.info/tag/indie-week/',
                 #  'https://getcomics.info/tag/image-week/'
                 ]

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'  # noqa: E501


def find_last_weekly(url):
    """Find las weekly post."""
    lastPost = url2soup(url).find('article', class_='type-post')
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
    postTitle = lastPost.h1.a.text
    postUrl = lastPost.h1.a['href']
    return postTitle, postUrl


def comics_list(url):
    """Get comics in a weekly pack."""
    weeklyUrl = find_last_weekly(url)[1]
    content = url2soup(weeklyUrl).select_one("section.post-contents")
    liste_a = content.find_all('a', style="color: #ff0000;")
    return get_href_with_name(liste_a, 'Download')


def _find_dl_buttons(url):
    """Find download buttons in a getcomics pages."""
    return url2soup(url).select("div.aio-pulse > a")


def down_com(url):
    """Find Zippyshare Button, find download url, download."""
    final_url = getfinalurl(url)
    print("Trying " + final_url)
    try:
        buttons = find_buttons(final_url)
        zippylink = find_zippy_button(buttons)
        finalzippy = check_url(zippylink)
    except ZippyButtonError as e:
        print(e)
        return
    except HTTPError as e:
        print("down_com got HTTPError")
        print(e)
        raise
    try:
        print(finalzippy)
        down_com_zippy(finalzippy)
    except Exception as e:
        print(e)
        print("error in down_com_zippy")


def down_com_zippy(url):
    """Download from zippyshare."""
    soup = url2soup(url)
    # Other beautiful soup selectors :
    # select("script[type='text/javascript']")
    # select("table[class='folderlogo'] > tr > td")[0]
    # find("div", style=re.compile("margin-left"))
    # find("script", type="text/javascript")
    # find("div", style=re.compile("width: 303px;"))
    # find("script", type="text/javascript")
    # downButton = soup.find('a', id="dlbutton").find_next_sibling().text
    downButton = soup.find('a', id="dlbutton").find_next_sibling().string
    try:
        fullURL, fileName = zpshare.get_file_url(url, downButton)
        print(f"Downloading from zippyshare into : {fileName}")
        r = requests.get(fullURL, stream=True)
        size = tools.bytes_2_human_readable(int(r.headers['Content-length']))
        print(size)
    except Exception as e:
        print(e)
        print("Can't get download link on zippyshare page")

    # Download from url & trim it a little bit
    with open(fileName, 'wb') as f:
        try:
            for block in r.iter_content(1024):
                f.write(block)
        except KeyboardInterrupt:
            pass
        except IOError:
            print("Error while writing file")
    r.close()
    print('Done\n--')
    return


def get_weekly_comics(mylist):
    """Compare remote and local list of comics and download."""
    print('Initialisation...')
    print('Je vais chercher les mots clés :')
    print(mylist)

    for url in getcomicsurls:
        # Other soup selectors
        # select_one("section.post-contents > ul")\
        # find_all('span', style="color: #ff0000;")
        remoteComicsList = comics_list(url)
        for newcomic in remoteComicsList:
            try:
                for myComic in mylist:
                    if myComic in newcomic:
                        down_com(newcomic)
                        pass
            except Exception as e:
                print(e)
                pass
    print("C'est tout. Vous pouvez fermer.")


def getresults(url):
    """Search Getcomics.

    Returns names and urls of posts returned by input url.
    """
    searchlist = []
    try:
        res = url2soup(url).select("div.post-info")
        for d in res:
            if d.h1.a.has_attr('href'):
                size = None
                searchsize = re.search(r'\d+ [KMGT]B', d.p.text, re.M | re.I)
                if searchsize:
                    size = searchsize.group(0)
                result = {"url": d.h1.a.get("href"),
                          "title": d.h1.a.text,
                          "size": size}
                searchlist.append(result)
        # print(searchlist)
    except HTTPError as e:
        print(e)
        print("something wrong happened")
    return searchlist


def searchurl(user_search, mode, page):
    """Return a getcomics research URL."""
    # Research with tag (https://getcomics.info/tag/......)
    if mode == 0:
        # Page 1 (no page number on this one)
        if page == 1:
            url = f"{tagsearch}{user_search.lower().replace(' ', '-')}"
        # Other pages
        else:
            url = (f"{tagsearch}{user_search.lower().replace(' ', '-')}"
                   f"/page/{page}/")
    # Classic research https://getcomics.info/?s=
    else:
        # Page 1
        if page == 1:
            # url = basesearch + '/?s=' + user_search.lower().replace(' ', '+')
            url = f"{basesearch}/?s={quote_plus(user_search.lower())}"
        # Other pages
        else:
            url = (f"{basesearch}/page/{page}/?s="
                   f"{quote_plus(user_search.lower())}")
    return url


def find_buttons(url):
    """Find download buttons in html soup, return list of buttons."""
    return url2soup(url).select("div.aio-pulse > a")


def find_zippy_button(buttons):
    """Find the button for zippyshare."""
    if not buttons:
        print("Empty list !")
        raise ZippyButtonError("Empty button list !")
    # found = False
    zippylink = None
    for button in buttons:
        # if 'zippyshare' in str(button).lower() \
        #       and 'href' in button.a.attrs:
        if 'zippyshare' in button.get("href") \
                or 'zippyshare' in button.get('title').lower():
            zippylink = button.get("href")
    if zippylink:
        return zippylink
    else:
        raise ZippyButtonError("No zippyshare button was found")


class ZippyButtonError(Exception):
    """Exception for zippyshare."""

    def __init__(self, msg):
        """Init error with msg."""
        super().__init__(self, msg)
