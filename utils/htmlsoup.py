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
    """Return hml soup.

    Args:
        url (str): url of page to scrape with bs4

    Returns:
        BeautifulSoup: soup of the page with the given URL
    """
    try:
        res: requests.Response = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        res.close()
        return soup
    except (ValueError, HTTPError) as e:
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
    return BeautifulSoup(html, 'html.parser')


def get_all_href(html: str, tag: str) -> list[str]:
    """Get a list of all links in specific tags in input html.

    Args:
        html (str): html
        tag (str): tag where to look for links inside

    Returns:
        list: list of URLS/links found
    """
    soup = html2soup(html)
    return [link['href'] for link in soup.find_all(tag) if link.has_attr('href')]


def get_href_with_name(liste_a: list | bs4.ResultSet, name: str) -> list[str]:
    """Get list of urls if text element is <name>"""
    return [a['href'] for a in liste_a if a.has_attr('href') and a.text == name]


def find_all_tag_with_class(html: str, tag: str, classname: str) -> bs4.element.ResultSet:
    """Get inner html from tag."""
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all(tag, class_=classname)


def find_all_tag(html: str, tag: str) -> bs4.element.ResultSet:
    """Find all 'tag' in html."""
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all(tag)
