#!/usr/bin/python3
# -*-coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests
import urllib.request
import urllib.error

# # get html from url
# def returnHTML(url):
#     user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
#     headers = { 'User-Agent' : user_agent }
#     #hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
#     try:
#         req = urllib.request.Request(url, None, headers)
#         response = urllib.request.urlopen(req)
#         html = response.read()
#         response.close()
#         return html
#     except ValueError as e:
#         print("returnHTML error")
#         print(e)
#         raise
#     except urllib.error.HTTPError as e:
#         print("returnHTML error")
#         print(e)
#         raise

#def url 2 soup
def url2soup(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    except ValueError as e:
             print("url2soup error")
             print(e)
             raise
    except urllib.error.HTTPError as e:
             print("url2soup error")
             print(e)
             raise
    except:
        print("Error in URL -> soup")
        raise

#get beautiful soup
def html2soup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def getaALLhref(html, tag):
    urllist = list()
    soup = html2soup(html)
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist
