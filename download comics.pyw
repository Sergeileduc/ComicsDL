#!/usr/bin/python3
# -*-coding:Utf-8 -
import sys
import re
import requests
import os
import time
import tkinter as tk
import urllib.request
import urllib.error
import threading
from bs4 import BeautifulSoup
import webbrowser

#getcomicsurl = "https://getcomics.info/tag/dc-week/"
#getcomicsurl = "http://getcomics.info/tag/marvel-now/"
#getcomicsurl = "https://getcomics.info/tag/indie-week/"
url = ''
basesearch = 'https://getcomics.info'
tagsearch = 'https://getcomics.info/tag/'
#basesearch = 'https://getcomics.info/?s=page/1/?s='

exit_thread= False
exit_success = False

substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '', ' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'', ' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '', ' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '', ' (Minutemen-Thoth)':''}

#DEBUG:
#open url
def OpenUrl(url):
    #webbrowser.open_new(url)
    webbrowser.open(url, new=0, autoraise=False)
    return

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

# get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    finalurl = urllib.request.urlopen(url).geturl()
    req = urllib.request.Request(finalurl, headers=hdr)
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


#get inner html from tag
def getTagClassData(html, tag, classname):
	soup = getSoup(html)
	list = soup.find_all(tag, class_=classname)
	return list

#get inner html from tag
def getTagData(html, tag, attr, name):
	soup = getSoup(html)
	list = soup.find_all(tag, {attr: name})
	return list


def getaALLhref(html, tag, classname):
    urllist = list()
    soup = getSoup(html)
    interm = soup.find_all(tag, class_=classname)
    for i in interm:
        a = i.find('a')
        if a.has_attr('href'):
            urllist.append(a['href'].replace('/#comments',''))
    return urllist


def namefromurl(url):
    return url.replace('https://getcomics.info/', '').replace('marvel/', '').replace('dc/', '').replace('/#comments', '')


#DL all comics in the liste
def downAllCom(liste):
    for dl in liste:
        downCom(dl[0])
    return

#find download link
def downCom(url):
    finalurl = urllib.request.urlopen(url).geturl()
    print ("Trying " + finalurl)
    zippylink = ''
    flag=False
    try:
        html = returnHTML(finalurl)
        downButtons = getTagClassData(html, 'div', 'aio-pulse')
        for button in downButtons:
            if 'zippyshare' in str(button).lower() and 'href' in button.a.attrs:
                #downComZippy(button.a['href'])
                zippylink = button.a['href']
                finalzippy = urllib.request.urlopen(zippylink).geturl()
                downComZippy(finalzippy)
                flag=False
            else:
                flag=True
        if flag==True:
            print("can't find zippyshare download button")
    except urllib.error.HTTPError:
        print("downCom got HTTPError from returnHTML")
        raise
    return

#download from zippyshare
def downComZippy(url):
	zippyHTML = returnHTML(url)
	#downButton = getTagClassData(zippyHTML, 'div', 'right')
	downButton = getTagData(zippyHTML, "script", "type", "text/javascript")
	try:
		fullURL, fileName = getZippyDL(url, downButton)
		print ("Download from zippyhare into : " + fileName)
		r = requests.get(fullURL)
	except:
		print("Can't get download link on zippyshare page")

	#download from url & trim it a little bit
	with open(fileName, 'wb') as f:
		try:
			for block in r.iter_content(1024):
				f.write(block)
		except KeyboardInterrupt:
			pass
		except IOError:
			print("Error while writing file")
	print ('Done\n--')
	return

# create url name list
def url_name_list(url):
    urlList = getaALLhref(returnHTML(url), 'li', 'post-meta-comments post-meta-align-left')
    searchlist = list()
    for url in urlList:
        searchlist.append((url, namefromurl(url)))
    return searchlist

def getZippyDL(url, button):
	print("Found zippyshare : " + url)

	#disassemble url
	comRawUrl0 = regexNightmare(button, '.*?getElementById.*?href = \"(.*?)\"');
	comRawUrl1 = regexNightmare(button, '.*?getElementById.*?href = \".*?\" \+ \((.*?)\) \+ \".*?\"\;');
	comRawUrl2 = regexNightmare(button, '.*?getElementById.*?href = \".*?\" \+ .*? \+ \"(.*?)\"\;');
	#filename = comRawUrl2[1:].replace('%20',' ').replace('%28','(').replace('%29',')').replace('%2c','')
	temp = replace(comRawUrl2[1:], substitutions1)
	filename = replace(temp, substitutions2)
	#calculating the id and forming url | that is an extremely dirty way, I know
	try:
		urlPattern = re.compile('(.*?) \% (.*?) \+ (.*?) \% (.*?)$', re.I)
		urlNum1 = urlPattern.search(str(comRawUrl1)).group(2)
		urlNum2 = urlPattern.search(str(comRawUrl1)).group(3)
		urlNum3 = urlPattern.search(str(comRawUrl1)).group(4)
		urlNumFull = (int(urlNum2) % int(urlNum1)) + (int(urlNum2) % int(urlNum3))
		fullURL = url[:-21] + comRawUrl0 + str(urlNumFull) + comRawUrl2
	except Exception as e:
		print("Mon erreur")
		print(e)
		raise
	return fullURL, filename

#just optimizing
def regexNightmare(html, regex):
	try:
		urlPattern = re.compile(regex, re.I)
		return urlPattern.search(str(html)).group(1)
	except:
		print("Cant't regex html")

def searchurl(user_search, mode, page):
    if mode == 0:
        if page == 1:
            url = tagsearch + user_search.lower().replace(' ', '-')
        else:
            url = tagsearch + user_search.lower().replace(' ', '-') + '/page/' + str(page) + '/'
    else:
        if page == 1:
            url = basesearch + '/?s=' + user_search.lower().replace(' ', '+')
        else:
            url = basesearch + '/page/' + str(page) + '/?s=' + user_search.lower().replace(' ', '+')
    return url

class Std_redirector(object):
    def __init__(self,widget):
        self.widget = widget

    def write(self,string):
        if not exit_thread:
            self.widget.insert(tk.END,string)
            self.widget.see(tk.END)

# our comicsList
class Getcomics(tk.Tk):
    deepbg='gray50'
    def __init__(self):
        super().__init__()
        width = 400
        self.page = 1
        self.usersearch = tk.StringVar()
        self.choices = ['Recherche par TAG', 'Recherche simple']
        self.mode = tk.StringVar()
        self.mode.set('Recherche simple')
        self.buttonlist = list()
        self.searchlist = list()
        self.downloadlist = list()
        self.mylist = list()
        self.title("Télécharger sur Getcomics v1")
        self.configure(background=self.deepbg)
        #topbar
        #topbar = tk.Frame(self, width=width, height=100, relief='groove', borderwidth=1)
        topbar = tk.Frame(self)
        #topbar.pack(expand=False, fill='both', side='top', anchor='n')
        topbar.pack()
        topbarleft = tk.Frame(topbar)
        #topbarleft.pack(side='left')
        topbarleft.grid(row=0, column=0, ipadx=20)
        topbarcenter = tk.Frame(topbar)
        #topbarcenter.pack(side='top')
        topbarcenter.grid(row=0, column=1)
        topbarright = tk.Frame(topbar)
        #topbarright.pack(side='right')
        topbarright.grid(row=0, column=2, ipadx=20)
        #left
        prevpage = tk.Button(topbarleft, text="page précédente", command=self.prevpage)
        prevpage.pack(fill=tk.Y)
        #right
        nextpage = tk.Button(topbarright, text="page suivante", command=self.nextpage)
        nextpage.pack()
        #center
        messageRecherche = tk.Label(topbarcenter, width=30, text="Rechercher sur Getcomics", justify=tk.CENTER,
                                    font=("Helvetica", 12))
        messageRecherche.pack()
        choice = tk.OptionMenu(topbarcenter, self.mode, *self.choices)
        choice.pack()
        search = tk.Entry(topbarcenter, width=30, bg='gray75', textvariable=self.usersearch ,font=("Verdana", 12))
        search.pack()
        search.focus_set()
        #

        #MainFrame
        MainFrame = tk.Frame(self, bg=self.deepbg)
        MainFrame.pack(padx=10, pady=10)
        #self.buttonframe = tk.Frame(MainFrame, width=width, height=200, relief='groove', borderwidth=0, padx=20, pady=20)
        self.buttonframe = tk.Frame(MainFrame, relief='groove', borderwidth=0, padx=20, pady=20)
        #self.buttonframe.pack(expand=True, fill='both', side='top', anchor='n')
        self.buttonframe.pack(side='left')

        instructions = tk.Label(self.buttonframe, text='Cliquez pour ajouter un élément à votre liste de téléchargement')
        instructions.pack()

        self.dlframe = tk.Frame(MainFrame, relief='groove', borderwidth=0, padx=20, pady=20)
        self.dlframe.pack(side='right', padx=(40,0))

        liste = tk.Label(self.dlframe, text="Liste de téléchargement\n.............")
        liste.pack(side='top')
        dlall = tk.Button(self.dlframe, text="Télécharger la liste", command=lambda: self.dlcom(self.downloadlist))
        dlall.pack(side='bottom')


        #output console
        bottombar = tk.Frame(self, width=width, height=100, relief='groove', borderwidth=1)
        bottombar.pack(expand=False, fill='both', side='bottom', anchor='n')
        self.output_text = tk.Text(bottombar, height=10, bg="black", fg="white")
        self.output_text.pack()
        sys.stdout = Std_redirector(self.output_text)

        #downCom(test_url)
        search.bind("<Return>", self.searchcomics)

        self.searchcomics(None)

    def destroylist(self, widgetlist):
        for w in widgetlist:
            w.destroy()
        widgetlist.clear()
        pass

    def searchcomics(self, event):
        self.searchlist.clear()
        self.destroylist(self.buttonlist)
        searchmode = self.choices.index(self.mode.get())
        self.searchlist = url_name_list(searchurl(self.usersearch.get(),searchmode, self.page))
        print(self.mode.get())
        #buttonlist = list()
        for i in self.searchlist:
            url=i[0]
            newButton = tk.Button(self.buttonframe, text=i[1].replace('-',' '), width=40, bg='RoyalBlue4', fg='white', relief='sunken', bd=0, font=("Verdana", 12))
            #newButton.config(command= lambda url=url: self.dlcom(url))
            newButton.config(command= lambda button=newButton: self.addtodl(button))
            newButton.pack()
            #print(i)
            self.buttonlist.append(newButton)
        #self.printwidgets(self.buttonlist)
        return

    def dlcom(self, liste):
        try:
            thread1 = threading.Thread(target=downAllCom, args=[liste])
            thread1.start()
        except:
            pass

    def addtodl(self, button):
        index = self.buttonlist.index(button)
        comic = button.cget('text')
        self.downloadlist.append((self.searchlist[index][0], self.searchlist[index][1]))
        newDL = tk.Label(self.dlframe, text=button.cget('text'))
        newDL.pack()


    def printwidgets(self, widegetlist):
        for w in widegetlist:
            print(str(w.cget('text')))

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def nextpage(self):
        self.page = self.page + 1
        self.searchcomics(None)

    def prevpage(self):
        if self.page > 1:
            self.page = self.page - 1
        else:
            self.page = 1
        self.searchcomics(None)



# class StartPage(tk.Frame):
#
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         label = tk.Label(self, text="Start Page", font=LARGE_FONT)
#         label.pack(pady=10, padx=10)
#

if __name__ == "__main__":
    app = Getcomics()  # constructor, calls method __init__
    app.mainloop()
