#!/usr/bin/python3
# -*-coding:Utf-8 -
import sys
import os
import re
import requests
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from datetime import datetime
import tkinter as tk
import tkinter.messagebox as msg
import sqlite3
import threading

exit_thread= False
exit_success = False
today = datetime.today().strftime("%Y-%m-%d")

#getcomicsurl = "https://getcomics.info/tag/dc-week/"
#getcomicsurl = "http://getcomics.info/tag/marvel-now/"
getcomicsurl = "https://getcomics.info/tag/indie-week/"

#myComicsList = ['batman', 'superman']
#myComicsList = ['deadpool', 'captain-america', 'x-men-gold']
#myComicsList = ['fathom', 'dark-ark']

substitutions1 = {'%2c': '', '%20': ' ', '%28': '(', '%29': ')'}
substitutions2 = {' (Digital)': '', ' (digital)': '', ' (Webrip)': '', ' (webrip)': '', ' (webrip-DCP)':'', ' (d_%27argh-Empire)': '', ' (Zone-Empire)': '', ' (Thornn-Empire)': '', ' (mv-DCP)': '', ' (The Last Kryptonian-DCP)': '', ' (GreenGiant-DCP)': '', ' (Minutemen-Thoth)':''}

today = datetime.today().strftime("%Y-%m-%d")

#multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

#get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent' : "Fiddler"}
    req = urllib.request.Request(url, headers=hdr)
    try:
        response = urllib.request.urlopen(req)
        html = response.read()
        return html
    except urllib.error.HTTPError as e:
        print (e.fp.read())
        raise

#get beautiful soup
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

def getaALLhref(html, tag):
    urllist = list()
    soup = getSoup(html)
    for link in soup.find_all('a'):
        if link.has_attr('href'):
            urllist.append(link['href'])
    return urllist

#find las weekly post
def findLastWeekly(htmlMain):
    lastPost = getTagClassData(htmlMain, 'article', 'type-post')[0]
    #check if today's archive is there, and retrieve its url
    print ("Latest weekly post: " + lastPost.time['datetime'])
    if today in lastPost.time['datetime']:
        #print ('There is a new one today. Hurrah!')
        pass
    else:
        #print ('Nothing yet. Exiting...')
        #print ('Continue anyway...')
        #quit()
        pass
    postUrl = lastPost.h1.a['href']
    return postUrl

#find download link
def downCom(url):
    finalurl = urllib.request.urlopen(url).geturl()
    print ("Found " + finalurl)
    zippylink = ''
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

#just optimizing
def regexNightmare(html, regex):
    try:
        urlPattern = re.compile(regex, re.I)
        return urlPattern.search(str(html)).group(1)
    except:
        print("Cant't regex html")

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

#download from zippyshare
def downComZippy(url):
    zippyHTML = returnHTML(url)
    #downButton = getTagClassData(zippyHTML, 'div', 'right')
    downButton = getTagData(zippyHTML, "script", "type", "text/javascript")
    try:
        fullURL, fileName = getZippyDL(url, downButton)
        print ("Downloading from " + fullURL + "\ninto : " + fileName)
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

def getWeeklyComics(mylist):
    print ('Initialisation...')
    print ('Je vais chercher les mots clés :')
    print (mylist)
    #get latest archive on the current page
    htmlMain = returnHTML(getcomicsurl)

    weeklyUrl = findLastWeekly(htmlMain)

    interm = getTagClassData(returnHTML(weeklyUrl), 'section', 'post-contents')
    interm2 = getTagClassData(str(interm), 'li', '')
    comList = getaALLhref(str(interm2), 'a')
    for newcomic in comList:
        try:
            for myComic in mylist:
                if myComic in newcomic:
                    downCom(newcomic)
                    pass
        except Exception as e:
            print(e)
            pass
    print("C'est tout. Vous pouvez fermer.")

class Std_redirector(object):
    def __init__(self,widget):
        self.widget = widget

    def write(self,string):
        if not exit_thread:
            self.widget.insert(tk.END,string)
            self.widget.see(tk.END)

#our comicsList
class MyComicsList(tk.Tk):
    def __init__(self, comic=None):
        super().__init__()

        #list MyComicsList[] initialisation
        if not comic:
            self.comic = []
        else:
            self.comic = comic

        w = 300 # width for the Tk
        h = 600 # height for the Tk
        # get screen width and height
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        longtext = "Ajoutez ou supprimez les séries à chercher dans le dernier post \n\"Indie week\" de Getcomics.info"
        # ascii_dctrad = """
        # ██████╗  ██████╗    ████████╗██████╗  █████╗ ██████╗
        # ██╔══██╗██╔════╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
        # ██║  ██║██║            ██║   ██████╔╝███████║██║  ██║
        # ██║  ██║██║            ██║   ██╔══██╗██╔══██║██║  ██║
        # ██████╔╝╚██████╗       ██║   ██║  ██║██║  ██║██████╔╝
        # ╚═════╝  ╚═════╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ """
        ascii_title = """
██████╗ ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗██╗ ██████╗███████╗
██╔════╝ ██╔════╝╚══██╔══╝██╔════╝██╔═══██╗████╗ ████║██║██╔════╝██╔════╝
██║  ███╗█████╗     ██║   ██║     ██║   ██║██╔████╔██║██║██║     ███████╗
██║   ██║██╔══╝     ██║   ██║     ██║   ██║██║╚██╔╝██║██║██║     ╚════██║
╚██████╔╝███████╗   ██║   ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║╚██████╗███████║
 ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝╚══════╝"""


#         ascii_cat = """
# ███╗   ███╗ █████╗ ██████╗ ██╗   ██╗███████╗██╗
# ████╗ ████║██╔══██╗██╔══██╗██║   ██║██╔════╝██║
# ██╔████╔██║███████║██████╔╝██║   ██║█████╗  ██║
# ██║╚██╔╝██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ██║
# ██║ ╚═╝ ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝
# """

#         ascii_cat = """
# ██████╗  ██████╗
# ██╔══██╗██╔════╝
# ██║  ██║██║
# ██║  ██║██║
# ██████╔╝╚██████╗
# ╚═════╝  ╚═════╝
# """

        ascii_cat = """
██╗███╗   ██╗██████╗ ██╗███████╗███████╗
██║████╗  ██║██╔══██╗██║██╔════╝██╔════╝
██║██╔██╗ ██║██║  ██║██║█████╗  ███████╗
██║██║╚██╗██║██║  ██║██║██╔══╝  ╚════██║
██║██║ ╚████║██████╔╝██║███████╗███████║
╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝╚══════╝╚══════╝
"""

        self.comic_canvas = tk.Canvas(self)
        self.message = tk.Label(self, text=longtext, anchor=tk.W, justify=tk.CENTER, wraplength = 250, font=("Helvetica", 12))
        self.asciititle = tk.Label(self, text=ascii_title, anchor=tk.W, justify=tk.LEFT, font=("Courier", 4))
        self.cat = tk.Label(self, text=ascii_cat, anchor=tk.W, justify=tk.LEFT, font=("Courier", 3))
        self.comic_frame = tk.Frame(self.comic_canvas)
        self.text_frame = tk.Frame(self)
        self.output_text = tk.Text(self, bg="black", fg="white")
        self.button = tk.Button(self, text="Télécharger les comics", command=self.run)
        self.scrollbar = tk.Scrollbar(self.comic_canvas, orient="vertical", command=self.comic_canvas.yview)
        self.comic_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.title("Télécharger Indé v2")
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.comic_create = tk.Text(self.text_frame, height=3, bg="white", fg="black")

        self.asciititle.pack()
        self.cat.pack()
        self.message.pack()
        self.comic_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_frame = self.comic_canvas.create_window((0, 0), window=self.comic_frame, anchor="n")

        #self.text_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_frame.pack()
        self.button.pack()
        self.comic_create.pack()
        self.output_text.pack(side=tk.BOTTOM, fill=tk.X)
        #self.button.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_idletasks()

        #self.comic_create.pack(side=tk.BOTTOM, fill=tk.X)

        self.comic_create.focus_set()

        self.colour_schemes = [{"bg": "lightgrey", "fg": "black"}, {"bg": "grey", "fg": "white"}]

        current_comic = self.load_comic()
        for comic in current_comic:
            comic_text = comic[0]
            self.add_comic(None, comic_text, True)

        self.bind("<Return>", self.add_comic)
        self.bind("<Configure>", self.on_frame_configure)
        self.bind_all("<MouseWheel>", self.mouse_scroll)
        self.bind_all("<Button-4>", self.mouse_scroll)
        self.bind_all("<Button-5>", self.mouse_scroll)
        self.comic_canvas.bind("<Configure>", self.comic_width)

    def run(self):
        sys.stdout = Std_redirector(self.output_text)
        current_comic = self.load_comic()
        comicslist = list()
        for row in current_comic:
            comicslist.append(row[0].lower().replace(' ','-'))
        thread1 = threading.Thread(target=getWeeklyComics, args=[comicslist])
        thread1.start()


    def add_comic(self, event=None, comic_text=None, from_db=False):
        if not comic_text:
            comic_text = self.comic_create.get(1.0, tk.END).strip()

        if len(comic_text) > 0:
            new_comic = tk.Label(self.comic_frame, text=comic_text, pady=10)

            self.set_comic_colour(len(self.comic), new_comic)

            new_comic.bind("<Button-1>", self.remove_comic)
            new_comic.pack(side=tk.TOP, fill=tk.X)

            self.comic.append(new_comic)

            if not from_db:
                self.save_comic(comic_text)

        self.comic_create.delete(1.0, tk.END)

    def remove_comic(self, event):
        comic = event.widget
        if msg.askyesno("Confirmation de suppressions", "Supprimer " + comic.cget("text") + "de la liste ?"):
            self.comic.remove(event.widget)

            delete_comic_query = "DELETE FROM comics_indies WHERE comic=?"
            delete_comic_data = (comic.cget("text"),)
            self.runQuery(delete_comic_query, delete_comic_data)

            event.widget.destroy()

            self.recolour_comic()

    def recolour_comic(self):
        for index, comic in enumerate(self.comic):
            self.set_comic_colour(index, task)

    def set_comic_colour(self, position, comic):
        _, comic_style_choice = divmod(position, 2)

        my_scheme_choice = self.colour_schemes[comic_style_choice]

        comic.configure(bg=my_scheme_choice["bg"])
        comic.configure(fg=my_scheme_choice["fg"])

    def on_frame_configure(self, event=None):
        self.comic_canvas.configure(scrollregion=self.comic_canvas.bbox("all"))

    def comic_width(self, event):
        canvas_width = event.width
        self.comic_canvas.itemconfig(self.canvas_frame, width = canvas_width)

    def mouse_scroll(self, event):
        if event.delta:
            self.comic_canvas.yview_scroll(-1*(event.delta/120), "units")
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1

            self.comic_canvas.yview_scroll(move, "units")

    def save_comic(self, comic):
        insert_comic_query = "INSERT INTO comics_indies VALUES (?)"
        insert_comic_data = (comic,)
        self.runQuery(insert_comic_query, insert_comic_data)

    def load_comic(self):
        load_comic_query = "SELECT comic FROM comics_indies"
        my_comic = self.runQuery(load_comic_query, receive=True)
        return my_comic

    @staticmethod
    def runQuery(sql, data=None, receive=False):
        conn = sqlite3.connect(".comics.db")
        cursor = conn.cursor()
        if data:
            cursor.execute(sql, data)
        else:
            cursor.execute(sql)

        if receive:
            return cursor.fetchall()
        else:
            conn.commit()

        conn.close()

    @staticmethod
    def firstTimeDB():
        #create_tables = "CREATE TABLE comics_dc (comic TEXT)"
        create_table1 = "CREATE TABLE IF NOT EXISTS comics_dc (comic TEXT)"
        MyComicsList.runQuery(create_table1)
        create_table2 = "CREATE TABLE IF NOT EXISTS comics_marvel (comic TEXT)"
        MyComicsList.runQuery(create_table2)
        create_table3 = "CREATE TABLE IF NOT EXISTS comics_indies (comic TEXT)"
        MyComicsList.runQuery(create_table3)

        default_comic_data = ("--- Ajoutez vos séries de comics ---",)
        default_dc_query = "INSERT INTO comics_dc VALUES (?)"
        MyComicsList.runQuery(default_dc_query, default_comic_data)
        default_marvel_query = "INSERT INTO comics_marvel VALUES (?)"
        MyComicsList.runQuery(default_marvel_query, default_comic_data)
        default_indie_query = "INSERT INTO comics_indies VALUES (?)"
        MyComicsList.runQuery(default_indie_query, default_comic_data)

#thread1 = threading.Thread(target=call_gen)

if __name__ == "__main__":
    if not os.path.isfile(".comics.db"):
        MyComicsList.firstTimeDB()
    comicsList = MyComicsList()
    comicsList.mainloop()