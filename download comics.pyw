#!/usr/bin/python3
# -*-coding:utf-8 -*-
import sys
import re
import requests
import os
import time
import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk
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
'(Digital)(TLK-EMPIRE-HD)':'', ' (Son of Ultron-Empire)':'', ' (BlackManta-Empire)':'',
' (Digital-Empire)':'', ' (2 covers)':'', ' GetComics.INFO':''}

defs={'KB':1024, 'MB':1024**2, 'GB':1024**3, 'TB':1024**4}

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

#convert to bytes
def convert2bytes(size):
    parts = size.split()
    size = parts[0]
    unit = parts[1]
    return int(size)*defs[unit]

def bytes_2_human_readable(number_of_bytes):
    if number_of_bytes < 0:
        raise ValueError("!!! number_of_bytes can't be smaller than 0 !!!")

    step_to_greater_unit = 1024.

    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'

    precision = 1
    number_of_bytes = round(number_of_bytes, precision)

    return str(number_of_bytes) + ' ' + unit

# get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    try:
        finalurl = urllib.request.urlopen(url).geturl()
        req = urllib.request.Request(finalurl, headers=hdr)
        response = urllib.request.urlopen(req)
        html = response.read()
        response.close()
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


def getresults(url):
    searchlist=list()
    try:
        soup=url2soup(url)
        for d in soup.select("div.post-info"):
            if d.h1.a.has_attr('href'):
                size = None
                searchsize = re.search( r'\d+ [KMGT]B', d.p.text, re.M|re.I)
                if searchsize:
                    size = searchsize.group(0)
                searchlist.append((d.h1.a.get("href"),d.h1.a.text, size))
        #print(searchlist)
        return searchlist
    except urllib.error.HTTPError:
        print("something wrong happened")


def getZippyDL(url, button):
	print("Found zippyshare : " + url)
	#disassemble url
	comRawUrl0 = regexNightmare(button, r'.*?getElementById.*?href = \"(.*?)\"')
	comRawUrl1 = regexNightmare(button, r'.*?getElementById.*?href = \".*?\" \+ \((.*?)\) \+ \".*?\"\;')
	comRawUrl2 = regexNightmare(button, r'.*?getElementById.*?href = \".*?\" \+ .*? \+ \"(.*?)\"\;')
	#filename = comRawUrl2[1:].replace('%20',' ').replace('%28','(').replace('%29',')').replace('%2c','')
	temp = replace(comRawUrl2[1:], substitutions1)
	filename = replace(temp, substitutions2)
	#calculating the id and forming url | that is an extremely dirty way, I know
	try:
		urlPattern = re.compile(r'(.*?) \% (.*?) \+ (.*?) \% (.*?)$', re.I)
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

    def flush(self):
        pass

# our comicsList
class Getcomics(tk.Tk):

    def __init__(self):
        def myfunction(event):
            dlcanva.configure(scrollregion=dlcanva.bbox("all"),width=200,height=200)
        super().__init__()
        sizex = 800 #largeur
        sizey = 600 #hauteur

        # Gets both half the screen width/height and window width/height
        posx = int(self.winfo_screenwidth()/2 - sizex/2)
        posy = int(self.winfo_screenheight()/2 - sizey/2)

        self.resultwidht=50
        self.dlwidth=40
        deepbg='#263238'
        color1='#37474F'
        #color2='#455A64'
        dark2='#37474F'
        dark3='#455A64'
        fg='white'
        style = ttk.Style()
        style.configure("deepBG.TFrame", foreground=fg, background=deepbg, border=0, relief='flat')
        style = ttk.Style()
        style.configure("dark1.TFrame", foreground=fg, background=color1, border=0, relief='flat', highlightthickness = 0)
        style = ttk.Style()
        style.configure("L.TLabel", foreground=fg, background=color1, relief='raised', font=("Verdana", 12))
        self.page = 1
        self.currentpercent = tk.IntVar()
        self.percent = tk.IntVar()
        self.dlbytes = tk.IntVar()
        self.currentpercent.set(0)
        self.percent.set(0)
        self.dlbytes.set(0)
        self.maxpercent = 100
        self.listsize = 0
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
        self.title("Télécharger sur Getcomics v2")
        self.configure(background=deepbg)

        topbar = ttk.Frame(self, style="deepBG.TFrame")
        mainframe = ttk.Frame(self, style="deepBG.TFrame")
        self.resultsframe = ttk.Frame(mainframe, style="dark1.TFrame")
        rightframe = ttk.Frame(mainframe, style="dark1.TFrame")
        buttonbar = ttk.Frame(self.resultsframe, style="deepBG.TFrame")

        bottombar = ttk.Frame(self, style="deepBG.TFrame")
        self.prevpage = tk.Button(buttonbar, text="page précédente", bg=dark3, fg=fg, font=("Verdana", 12), relief='raised', border=2, highlightthickness = 0, command=self.gotoprevpage)
        nextpage = tk.Button(buttonbar, text="page suivante", bg=dark3, fg=fg, font=("Verdana", 12), relief='raised', border=2, highlightthickness = 0, command=self.gotonextpage)
        #messageRecherche = tk.Label(topbar, text="Rechercher sur Getcomics", bg=dark2, fg=fg, justify=tk.CENTER,
        #                            font=("Helvetica", 12))
        choice = tk.OptionMenu(topbar, self.mode, *self.choices)
        choice.config(bg=dark3, fg=fg, relief='flat', border=0, highlightthickness = 0)
        choice["menu"].config(bg=dark3, fg=fg, relief='flat', border=0)
        search = tk.Entry(topbar, width=self.resultwidht, justify='center', insertbackground=fg, bg=dark2,fg=fg, textvariable=self.usersearch ,font=("Verdana", 12))

        dlcanva = tk.Canvas(rightframe, bg=color1, highlightthickness = 0)
        self.dlframe = ttk.Frame(dlcanva, style="dark1.TFrame")
        scrollbar = ttk.Scrollbar(dlcanva, orient="vertical", command=dlcanva.yview)
        instructions = ttk.Label(self.resultsframe, style="L.TLabel", text='Cliquez pour ajouter un élément à votre liste de téléchargement')
        liste = tk.Label(rightframe, width=self.dlwidth, bg=dark2, fg=fg, relief='raised', text="Liste de téléchargement", font=("Verdana", 12))
        dlall = tk.Button(rightframe, bg=color1, fg=fg, highlightthickness = 0, text="Télécharger la liste", font=("Verdana", 12, 'bold'), command=lambda: self.dlcom(self.downloadlist))

        outputtext = tkst.ScrolledText(bottombar, height=8, bg='black', fg='white', wrap = tk.WORD)
        self.progress = ttk.Progressbar(bottombar, orient="horizontal", variable=self.currentpercent, mode="determinate")
        self.progress2 = ttk.Progressbar(bottombar, orient="horizontal", variable=self.percent, mode="determinate")

        topbar.pack(fill='x', anchor='n', padx=20, pady=20)
        mainframe.pack(fill='both', expand=1, anchor='nw', padx=20, pady=(0,5))
        self.resultsframe.pack(side='left', anchor='nw', fill='both', expand = 1, padx=(0,20))
        rightframe.pack(side='left', anchor='ne', fill='y', expand = 1)
        buttonbar.pack(side='bottom', anchor='sw', fill='x', expand=1)

        nextpage.pack(side='right', padx=(0,50))
        search.pack(side='left')
        choice.pack(side='right')
        search.focus_set()
        search.bind("<Return>", self.searchcomics)
        instructions.pack(fill='x')
        liste.pack(fill='x')
        dlcanva.pack(fill='both', expand=1)
        scrollbar.pack(side = 'right', fill = 'y')
        dlcanva.configure(yscrollcommand=scrollbar.set)
        dlcanva.create_window((0,0),window=self.dlframe, anchor='nw')
        self.dlframe.bind("<Configure>",myfunction)
        dlall.pack(fill='x', side='bottom')


        bottombar.pack(fill='x')
        self.progress.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
        self.progress2.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
        outputtext.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
        sys.stdout = Std_redirector(outputtext)

        self.searchcomics(None)


    def destroylist(self, widgetlist):
        for w in widgetlist:
            w.destroy()
        widgetlist.clear()
        pass


    #search comics function
    def searchcomics(self, event):
        dark2='#546E7A'
        fg='#FAFAFA'
        self.searchlist.clear()
        self.destroylist(self.buttonlist)
        searchmode = self.choices.index(self.mode.get())
        self.searchlist = getresults(searchurl(self.usersearch.get(),searchmode, self.page))
        #buttonlist = list()
        for i in self.searchlist:
            title = i[1] + ' (' + str(i[2]) + ')'
            newButton = tk.Button(self.resultsframe, text=title, width=self.resultwidht, bg=dark2, fg=fg, relief='flat', border=0, highlightthickness = 0, font=("Verdana", 10))
            newButton.config(command= lambda button=newButton: self.addtodl(button))
            newButton.pack(fill='both', expand=1, pady=0)
            self.buttonlist.append(newButton)
        return

    #download one comic
    def dlcom(self, liste):
        try:
            thread1 = threading.Thread(target=self.downAllCom, args=[liste])
            thread1.start()
        except:
            print("Problem")
            pass


    #click to add to DL list
    def addtodl(self, button):
        dark2='#546E7A'
        fg='#FAFAFA'
        index = self.buttonlist.index(button)
        comic = button.cget('text')
        if comic not in (item[1] for item in self.downloadlist):
            if self.searchlist[index][2] != None:
                bytes = convert2bytes(self.searchlist[index][2])
                self.listsize += bytes
            newDL = tk.Button(self.dlframe, text=button.cget('text').title(), width=self.resultwidht, anchor='w', bg=dark2, fg=fg, relief='flat', border=0, highlightthickness = 0, font=("Verdana", 10))
            newDL.config(command= lambda button=newDL: self.removedl(button))
            newDL.pack(fill='both', expand=1, pady=0)
            self.downloadlist.append((self.searchlist[index][0], self.searchlist[index][1], newDL, self.searchlist[index][2]))
            print("Taille de la file d'attente (donnée indicative) : " + bytes_2_human_readable(self.listsize))
        else:
            print("Already in your DL list")


    #click to remove an item function
    def removedl(self, button):
        for i in self.downloadlist:
            if button == i[2]:
                if i[3] != None:
                    bytes = convert2bytes(i[3])
                    self.listsize -= bytes
                self.downloadlist.remove(i)
        button.destroy()
        print("Taille de la file d'attente (donnée indicative) : " + bytes_2_human_readable(self.listsize))


    #DL all comics in the liste
    def downAllCom(self, liste):
        self.dlbytes.set(0)
        for dl in liste:
            self.downCom(dl[0])
        print("Terminé, vous pouvez quitter")
        return


    #find download link
    def downCom(self, url):
        finalurl = urllib.request.urlopen(url).geturl()
        print ("Trying " + finalurl)
        zippylink = ''
        try:
            soup=url2soup(finalurl)
            downButtons = soup.select("div.aio-pulse > a")
            for button in downButtons:
                #if 'zippyshare' in str(button).lower() and 'href' in button.a.attrs:
                if 'zippyshare' in button.get("href") or 'zippyshare' in button.get('title').lower():
                    zippylink = button.get("href")
                    try:
                        finalzippy = urllib.request.urlopen(zippylink).geturl()
                        self.downComZippy(finalzippy)
                    except IOError:
                        print("Zippyhare download failed")
        except urllib.error.HTTPError:
            print("downCom got HTTPError from returnHTML")
            raise
        return


    #download from zippyshare
    def downComZippy(self, url):
        self.progress["value"] = 0
        soup=url2soup(url)
        downButton = soup.select('script[type="text/javascript"]')
        try:
            fullURL, fileName = getZippyDL(url, downButton)
            print ("Download from zippyhare into : " + fileName)
            r = requests.get(fullURL, stream=True)
            size = int(r.headers['Content-length']) #size in bytes
        except:
            print("Can't get download link on zippyshare page")

        #download from url & trim it a little bit
        with open(fileName, 'wb') as f:
            try:
                dl = 0
                if self.listsize == 0:
                    self.listsize = 1
                for block in r.iter_content(51200):
                    dl += len(block)
                    self.currentpercent.set(int(100 * dl / size))
                    self.dlbytes.set(self.dlbytes.get() + len(block))
                    self.percent.set(int(100 * self.dlbytes.get() / self.listsize))
                    f.write(block)
            except KeyboardInterrupt:
                pass
            except IOError:
                print("Error while writing file")
            print ('Done\n--')
        return


    #nexpage button function
    def gotonextpage(self):
        self.page = self.page + 1
        self.searchcomics(None)
        self.prevpage.pack(side='left', padx=(50,0))

    #previous page button function
    def gotoprevpage(self):
        if self.page > 1:
            self.page = self.page - 1
            self.prevpage.pack_forget()
        else:
            self.page = 1
        self.searchcomics(None)


if __name__ == "__main__":
    app = Getcomics()  # constructor, calls method __init__
    app.mainloop()
