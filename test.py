#!/usr/bin/python3
# -*-coding:Utf-8 -
import re
import requests
import os
import time
import tkinter as tk
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

file = 'soup.html'
url = ''
basesearch = 'https://getcomics.info/?s='
tagsearch = 'https://getcomics.info/tag/'
#basesearch = 'https://getcomics.info/?s=page/1/?s='


# mylist = list()
# get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req)
        html = response.read()
        return html
    except urllib.error.HTTPError as e:
        print(e.fp.read())
        raise


# get beautiful soup
def getSoup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def writesoup(soup):
    with open(file, 'w') as f_out:
        f_out.write(soup)
    pass


# get inner html from tag
def getTagClassData(soup, tag, classname):
    list = soup.find_all(tag, class_=classname)
    return list


def getaALLhref(html, tag, classname):
    urllist = list()
    soup = getSoup(html)
    interm = soup.find_all(tag, class_=classname)
    for i in interm:
        a = i.find('a')
        if a.has_attr('href'):
            urllist.append(a['href'])
    return urllist


def namefromurl(url):
    return url.replace('https://getcomics.info/', '').replace('marvel/', '').replace('dc/', '').replace('/#comments',
                                                                                                        '')

# create url name list
def url_name_list(url):
    urlList = getaALLhref(returnHTML(url), 'li', 'post-meta-comments post-meta-align-left')
    mylist = list()
    for url in urlList:
        mylist.append((url, namefromurl(url)))
    return mylist


def searchurl(user_search, mode):
    url = 'https://getcomics.info/'
    if mode == 0:
        url = tagsearch + user_search.lower().replace(' ', '-')
        print ("URL de recherche getcomics : " + url)
    else:
        url = basesearch + user_search.lower().replace(' ', '-')
        print ("URL de recherche getcomics : " + url)
    return url



# our comicsList
class Getcomics(tk.Tk):
    def __init__(self):
        super().__init__()
        width = 500
        self.usersearch = tk.StringVar()
        self.choices = ['Recherche par TAG', 'Recherche simple']
        self.mode = tk.StringVar()
        self.mode.set('Recherche par TAG')
        self.buttonlist = list()
        self.title("Télécharger sur Getcomics v1")
        self.configure(background='SteelBlue3')
        topbar = tk.Frame(self, width=width, bg='SteelBlue4', height=100, relief='groove', borderwidth=1)
        topbar.pack(expand=False, fill='both', side='top', anchor='n')
        self.buttonframe = tk.Frame(self, width=width, height=200, bg='SteelBlue4', relief='groove', borderwidth=0, padx=20, pady=20)
        self.buttonframe.pack(expand=True, fill='both', side='top', anchor='n')
        bottombar = tk.Frame(self, width=width, height=100, bg='SteelBlue4', relief='groove', borderwidth=1)
        bottombar.pack(expand=False, fill='both', side='bottom', anchor='n')
        messageRecherche = tk.Label(bottombar, width=30, text="Rechercher sur Getcomics", bg='SteelBlue4', fg='white', justify=tk.CENTER,
                                    font=("Helvetica", 12))
        messageRecherche.pack()
        choice = tk.OptionMenu(bottombar, self.mode, *self.choices)
        choice.pack()
        search = tk.Entry(bottombar, width=10, textvariable=self.usersearch ,font=("Verdana", 12))
        search.pack()
        search.focus_set()
        search.bind("<Return>", self.searchcomics)


    def destroylist(self, widgetlist):
        for w in widgetlist:
            w.destroy()
        widgetlist.clear()
        pass

    def searchcomics(self, event):
        self.destroylist(self.buttonlist)
        searchmode = self.choices.index(self.mode.get())
        print(searchmode)
        mylist = url_name_list(searchurl(self.usersearch.get(),searchmode))
        print(self.mode.get())
        #buttonlist = list()
        for i in mylist:
            newButton = tk.Button(self.buttonframe, text=i[1], width=40, font=("Verdana", 12))
            newButton.pack()
            self.buttonlist.append(newButton)
        self.printwidgets(self.buttonlist)
        return

    def printwidgets(self, widegetlist):
        for w in widegetlist:
            print(str(w.cget('text')))

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # populate app
    # def populate():
    #     if url != '':
    #         mylist = url_name_list(url)
    #     else:
    #         mylist = list()
    #
    #     buttonlist = list()
    #     for i in mylist:
    #         newButton = tk.Button(buttonframe, text=i[1], width=40)
    #         newButton.pack()
    #     return buttonlist


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)


if __name__ == "__main__":
    app = Getcomics()  # constructor, calls method __init__
    app.mainloop()
