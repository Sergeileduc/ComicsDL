#!/usr/bin/python3
# -*-coding:Utf-8 -
import sys
import re
import requests
import os
import time
import tkinter as tk
import tkinter.scrolledtext as tkst
import urllib.request
import urllib.error
import threading
from bs4 import BeautifulSoup

url = ''
basesearch = 'https://getcomics.info'
tagsearch = 'https://getcomics.info/tag/'

exit_thread= False
exit_success = False

substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '',
' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'',
' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '',
' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '',
' (Minutemen-Thoth)':'', ' (Glorith-HD)':'', ' (Oroboros-DCP)':'',
'(Digital)(TLK-EMPIRE-HD)':'', ' (Son of Ultron-Empire)':''}

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

# get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    try:
        finalurl = urllib.request.urlopen(url).geturl()
        req = urllib.request.Request(finalurl, headers=hdr)
        response = urllib.request.urlopen(req)
        html = response.read()
        req.close()
        return html
    except ValueError as e:
        print(e)
        raise
    except urllib.error.HTTPError as e:
        print(e)
        raise

#def url 2 soup
def url2soup(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup
    except:
        print("Error")
        raise

# get beautiful soup
def getSoup(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


#get inner html from tag
# def getTagClassData(html, tag, classname):
# 	soup = getSoup(html)
# 	list = soup.find_all(tag, class_=classname)
# 	return list

#get inner html from tag
# def getTagData(html, tag, attr, name):
# 	soup = getSoup(html)
# 	list = soup.find_all(tag, {attr: name})
# 	return list

def getresults(url):
    searchlist=list()
    try:
        # soup=getSoup(returnHTML(url))
        # interm = soup.find_all('h1', class_='post-title')
        # soup2=getSoup(str(interm))
        # list2=soup2.find_all('a')
        # for a in list2:
        #     if a.has_attr('href'):
        #         searchlist.append(((a['href']), str(a.text)))
        soup=url2soup(url)
        for a in soup.select("h1.post-title > a"):
            if a.has_attr('href'):
                searchlist.append((a.get("href"),a.text))
        return searchlist
    except:
        print("something wrong happened")

#DL all comics in the liste
def downAllCom(liste):
    for dl in liste:
        downCom(dl[0])
    print("Terminé, vous pouvez quitter")
    return

#find download link
def downCom(url):
    finalurl = urllib.request.urlopen(url).geturl()
    print ("Trying " + finalurl)
    zippylink = ''
    flag=False
    try:
        #html = returnHTML(finalurl)
        #downButtons = getTagClassData(html, 'div', 'aio-pulse')
        soup=url2soup(finalurl)
        downButtons = soup.select("div.aio-pulse > a")
        for button in downButtons:
            #if 'zippyshare' in str(button).lower() and 'href' in button.a.attrs:
            if 'zippyshare' in button.get("href") or 'zippyshare' in button.get('title').lower():
                #downComZippy(button.a['href'])
                #zippylink = button.a['href']
                zippylink = button.get("href")
                try:
                    finalzippy = urllib.request.urlopen(zippylink).geturl()
                    downComZippy(finalzippy)
                except:
                    print("Zippyhare download failed")
                    flag=False
            # elif 'download now' in button.get('title').lower():
            #     print("can't find or open zippyshare download button\nTrying 'Download now button'")


    except urllib.error.HTTPError:
        print("downCom got HTTPError from returnHTML")
        raise
    return

#download from zippyshare
def downComZippy(url):
    #zippyHTML = returnHTML(url)
    #downButton = getTagClassData(zippyHTML, 'div', 'right')
    #downButton = getTagData(zippyHTML, "script", "type", "text/javascript")
    soup=url2soup(url)
    downButton = soup.select('script[type="text/javascript"]')
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

def downlaodnow(url):
    pass

#just optimizing
def regexNightmare(html, regex):
	try:
		urlPattern = re.compile(regex, re.I)
		return urlPattern.search(str(html)).group(1)
	except:
		print("Cant't regex html")

#returns a getcomics research URL
def searchurl(user_search, mode, page):
    #research with tag (https://getcomics.info/tag/......)
    if mode == 0:
        #page 1 (no page number on this one)
        if page == 1:
            url = tagsearch + user_search.lower().replace(' ', '-')
        #other pages
        else:
            url = tagsearch + user_search.lower().replace(' ', '-') + '/page/' + str(page) + '/'
    #classic research https://getcomics.info/?s=
    else:
        #page 1
        if page == 1:
            url = basesearch + '/?s=' + user_search.lower().replace(' ', '+')
        #other pages
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

    def __init__(self):
        def myfunction(event):
            dlcanva.configure(scrollregion=dlcanva.bbox("all"),width=200,height=200)
        super().__init__()
        sizex = 800 #largeur
        sizey = 500 #hauter
        posx  = 400
        posy  = 100
        self.resultwidht=50
        self.dlwidth=40
        deepbg='#263238'
        dark2='#37474F'
        dark3='#455A64'
        fg='white'
        self.page = 1
        self.usersearch = tk.StringVar()
        self.choices = ['Recherche par TAG', 'Recherche simple']
        self.mode = tk.StringVar()
        self.mode.set('Recherche simple')
        self.usersearch = tk.StringVar()
        self.buttonlist = list()
        self.searchlist = list()
        self.downloadlist = list()
        self.mylist = list()
        self.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
        self.title("Télécharger sur Getcomics v1")
        self.configure(background=deepbg)

        topbar = tk.Frame(self, bg=dark2)
        topbarleft = tk.Frame(topbar, bg=dark2)
        topbarcenter = tk.Frame(topbar, bg=dark2)
        topbarright = tk.Frame(topbar, bg=dark2)
        bottombar = tk.Frame(self,bg=deepbg)
        prevpage = tk.Button(topbarleft, text="page précédente", bg=dark3, fg=fg, font=("Verdana", 12), relief='raised', border=2, highlightthickness = 0, command=self.prevpage)
        nextpage = tk.Button(topbarright, text="page suivante", bg=dark3, fg=fg, font=("Verdana", 12), relief='raised', border=2, highlightthickness = 0, command=self.nextpage)
        messageRecherche = tk.Label(topbarcenter, text="Rechercher sur Getcomics", bg=dark2, fg=fg, justify=tk.CENTER,
                                    font=("Helvetica", 12))
        choice = tk.OptionMenu(topbarcenter, self.mode, *self.choices)
        choice.config(bg=dark3, fg=fg, relief='flat', border=0, highlightthickness = 0)
        choice["menu"].config(bg=dark3, fg=fg, relief='flat', border=0)
        search = tk.Entry(topbarcenter, width=30, justify='center', insertbackground=fg, bg=deepbg,fg=fg, textvariable=self.usersearch ,font=("Verdana", 12))

        mainframe = tk.Frame(self, bg=deepbg, border=0, relief='flat')
        self.resultsframe = tk.Frame(mainframe, bg=dark2, border=0, relief='flat')
        rightframe = tk.Frame(mainframe, bg=dark2, highlightthickness = 0)
        dlcanva = tk.Canvas(rightframe, bg=dark2, highlightthickness = 0)
        self.dlframe = tk.Frame(dlcanva, bg=dark2, border=0, relief='flat')
        scrollbar = tk.Scrollbar(dlcanva, orient="vertical", command=dlcanva.yview)
        instructions = tk.Label(self.resultsframe, bg=dark2, fg=fg, relief='raised', text='Cliquez pour ajouter un élément à votre liste de téléchargement', font=("Verdana", 12))
        liste = tk.Label(rightframe, width=self.dlwidth, bg=dark2, fg=fg, relief='raised', text="Liste de téléchargement", font=("Verdana", 12))
        dlall = tk.Button(rightframe, bg=dark2, fg=fg, highlightthickness = 0, text="Télécharger la liste", font=("Verdana", 12, 'bold'), command=lambda: self.dlcom(self.downloadlist))

        outputtext = tkst.ScrolledText(bottombar, height=8, bg='black', fg='white', wrap = tk.WORD)

        topbar.pack(fill='x', anchor='n', padx=20, pady=(10,5))
        topbarleft.pack(side='left')
        topbarcenter.pack(side='left', fill='x', expand=1, padx=50)
        topbarright.pack(side='left')
        prevpage.pack(padx=(10,0))
        nextpage.pack(padx=(0,10))
        #messageRecherche.pack(fill='x', expand=1)
        search.pack(side='left', padx=(0,30))
        choice.pack(side='left')
        search.focus_set()
        search.bind("<Return>", self.searchcomics)
        mainframe.pack(fill='both', expand=1, anchor='nw', padx=20, pady=(0,5))
        self.resultsframe.pack(side='left', anchor='nw', fill='both', expand = 1)
        rightframe.pack(side='left', anchor='ne', fill='y', expand = 1)
        instructions.pack(fill='x')
        liste.pack(fill='x')
        dlcanva.pack(fill='both', expand=1)
        scrollbar.pack(side = 'right', fill = 'y')
        dlcanva.configure(yscrollcommand=scrollbar.set)
        dlcanva.create_window((0,0),window=self.dlframe, anchor='nw')
        self.dlframe.bind("<Configure>",myfunction)
        dlall.pack(fill='x', side='bottom')


        bottombar.pack(fill='x')
        outputtext.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
        sys.stdout = Std_redirector(outputtext)


        self.searchcomics(None)

    def destroylist(self, widgetlist):
        for w in widgetlist:
            w.destroy()
        widgetlist.clear()
        pass

    def searchcomics(self, event):
        dark2='#546E7A'
        fg='#FAFAFA'
        self.searchlist.clear()
        self.destroylist(self.buttonlist)
        searchmode = self.choices.index(self.mode.get())
        self.searchlist = getresults(searchurl(self.usersearch.get(),searchmode, self.page))
        #buttonlist = list()
        for i in self.searchlist:
            url=i[0]
            #newButton = tk.Button(self.buttonframe, text=i[1].replace('-',' ').title(), width=40, bg='RoyalBlue4', fg='white', relief='sunken', bd=0, font=("Verdana", 12))
            newButton = tk.Button(self.resultsframe, text=i[1], width=self.resultwidht, bg=dark2, fg=fg, relief='flat', border=0, highlightthickness = 0, font=("Verdana", 10))
            #newButton.config(command= lambda url=url: self.dlcom(url))
            newButton.config(command= lambda button=newButton: self.addtodl(button))
            newButton.pack(fill='both', expand=1, pady=0)
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
        dark2='#546E7A'
        fg='#FAFAFA'
        index = self.buttonlist.index(button)
        comic = button.cget('text')
        newDL = tk.Button(self.dlframe, text=button.cget('text').title(), width=self.resultwidht, bg=dark2, fg=fg, relief='flat', border=0, highlightthickness = 0, font=("Verdana", 10))
        newDL.config(command= lambda button=newDL: self.removedl(button))
        newDL.pack(fill='both', expand=1, pady=0)
        self.downloadlist.append((self.searchlist[index][0], self.searchlist[index][1], newDL))


    def removedl(self, button):
        for i in self.downloadlist:
            if button == i[2]:
                self.downloadlist.remove(i)
        button.destroy()


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
