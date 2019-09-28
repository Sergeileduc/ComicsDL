#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to use requests and BeautifulSoup."""

from bs4 import BeautifulSoup  # html parser
import requests
from requests.exceptions import HTTPError


def url2soup(url):
    """Return hml soup."""
    try:
        res = requests.get(url)
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


def html2soup(html):
    """Get beautiful soup (html parser)."""
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_all_href(html, tag):
    """Get a lit of all links in input html."""
    urllist = list()
    soup = html2soup(html)
    for link in soup.find_all(tag):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist


def get_href_with_name(liste_a, name):
    """Get href urls based text."""
    urllist = list()
    for a in liste_a:
        if a.has_attr('href') and a.text == name:
            urllist.append(a['href'])
    return urllist


def get_tag_data(html, tag, classname):
    """Get inner html from tag."""
    soup = BeautifulSoup(html, 'html.parser')
    # prettysoup = soup.prettify()
    my_list = soup.find_all(tag, class_=classname)
    return my_list


def get_all_tag(html, tag):
    """Find all 'tag' in html."""
    soup = BeautifulSoup(html, 'html.parser')
    my_list = soup.find_all(tag)
    return my_list
