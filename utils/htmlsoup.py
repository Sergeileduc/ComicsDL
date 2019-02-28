#!/usr/bin/python3
# -*-coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests
import urllib.request
import urllib.error


# Def url 2 soup
def url2soup(url):
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
    except urllib.error.HTTPError as e:
        print("url2soup error")
        print(e)
        raise
    except Exception as e:
        print(e)
        print("Error in URL -> soup")
        raise


# Get beautiful soup
def html2soup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


# Get a lit of all links in input html
def getaALLhref(html, tag):
    urllist = list()
    soup = html2soup(html)
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist
