#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to use requests and BeautifulSoup."""

import bs4
from bs4 import BeautifulSoup  # html parser
import requests
from requests.exceptions import HTTPError

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'  # noqa: E501
headers = {'user-agent': user_agent}


def url2soup(url: str) -> BeautifulSoup:
    """Return hml soup."""
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        res.close()
        return soup
    except ValueError as e:
        print("url2soup error")
        print(e)
        raise
    except HTTPError as e:
        print("url2soup error")
        print(e)
        raise
    except Exception as e:
        print(e)
        print("Error in URL -> soup")
        raise


def html2soup(html: str) -> BeautifulSoup:
    """Get beautiful soup (html parser).

    Args:
        html (str)

    Returns:
        BeautifulSoup
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_all_href(html: str, tag: str) -> list[str]:
    """Get a list of all links in specific tags in input html.

    Args:
        html (str): html
        tag (str): tag where to look for links inside

    Returns:
        list: list of URLS/links found
    """
    urllist = []
    soup = html2soup(html)
    for link in soup.find_all(tag):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist


def get_href_with_name(liste_a: list | bs4.ResultSet, name: str) -> list[str]:
    """Get list of urls if text element is <name>"""
    urllist = []
    for a in liste_a:
        if a.has_attr('href') and a.text == name:
            urllist.append(a['href'])
    return urllist


def find_all_tag_with_class(html: str, tag: str, classname: str) -> list:
    """Get inner html from tag."""
    soup = BeautifulSoup(html, 'html.parser')
    my_list = soup.find_all(tag, class_=classname)
    return my_list


def find_all_tag(html: str, tag: str) -> list:
    """Find all 'tag' in html."""
    soup = BeautifulSoup(html, 'html.parser')
    my_list = soup.find_all(tag)
    return my_list
