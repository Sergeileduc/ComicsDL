#!/usr/bin/python3
# -*-coding:Utf-8 -*
#import io
import base64
import requests
import io
import re
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import font as tkfont # python 3
import urllib.request as urllib2
from bs4 import BeautifulSoup
import webbrowser

url = 'http://www.dctrad.fr/index.php'
dctradpage = 'http://www.dctrad.fr/index.php'
coverlist = list()
urllist = list()
imagebytes_list = list()
data_stream_list = list()
pil_image_list = list()
photo = list()
#
cat_list = ['http://www.dctrad.fr/images/icons/forum/RebirthK.png','http://www.dctrad.fr//images/icons/forum/dccomicsv2.png', 'http://www.dctrad.fr//images/icons/forum/IconindiedctK.png', 'http://www.dctrad.fr/images/icons/forum/MarvelK.png']
cat_byte_list = list()
cat_data_stream_list = list()
cat_pil_list = list()
cat_image_list = list()

#open url
def OpenUrl(url):
    #webbrowser.open_new(url)
    webbrowser.open(url, new=0, autoraise=False)
    return

#get html from url
def returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent' : "Fiddler"}
    req = urllib2.Request(url, headers=hdr)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        print (e.fp.read())
    html = response.read()
    return html

#get inner html from tag
def getTagData(html, tag, classname):
    soup = BeautifulSoup(html, 'html.parser')
    prettysoup = soup.prettify()
    list = soup.find_all(tag, class_=classname)
    return list

def getAllTag(html, tag):
    soup=BeautifulSoup(html, 'html.parser')
    list = soup.find_all(tag)
    return list

def getCatCovers():
    #catégories images
    global cat_image_list
    global cat_byte_list
    global cat_data_stream_list
    global cat_pil_list
    for cover in cat_list:
        cat_byte_list.append(urllib2.urlopen(cover).read())
    for imagebyte in cat_byte_list:
        cat_data_stream_list.append(io.BytesIO(imagebyte))
    for data_stream in cat_data_stream_list:
        cat_pil_list.append(Image.open(data_stream))
    #cat
    cat_image_list.append(ImageTk.PhotoImage(cat_pil_list[0]))
    cat_image_list.append(ImageTk.PhotoImage(cat_pil_list[1]))
    cat_image_list.append(ImageTk.PhotoImage(cat_pil_list[2]))
    cat_image_list.append(ImageTk.PhotoImage(cat_pil_list[3]))
    return

def getHeaderCovers():
    #catégories images
    global coverlist
    global imagebytes_list
    global data_stream_list
    global pil_image_list
    for cover in coverimgurl:
        imagebytes_list.append(urllib2.urlopen(cover).read())
    for imagebyte in imagebytes_list:
        data_stream_list.append(io.BytesIO(imagebyte))
    for data_stream in data_stream_list:
        pil_image_list.append(Image.open(data_stream))
    #cat
    for image in pil_image_list:
        photo.append(ImageTk.PhotoImage(image))
    return

def getUrls():
    global urllist
    for a in comicslist:
        if a.has_attr('href'):
            urllist.append(a['href'])
    return

def refresh():
    html = returnHTML(dctradpage)
    soup = BeautifulSoup(html, 'html.parser')
    headerlist = soup.find_all('span', class_="btn-cover")
    comicslist = soup.select('span.btn-cover a')
    coverlist = soup.select('span.btn-cover img')
    getCatCovers()
    getHeaderCovers()
    getUrls()
    return

html = returnHTML(dctradpage)
soup = BeautifulSoup(html, 'html.parser')
headerlist = soup.find_all('span', class_="btn-cover")
comicslist = soup.select('span.btn-cover a')
coverlist = soup.select('span.btn-cover img')


coverimgurl = list()
for img in coverlist:
    coverimgurl.append(img['src'])

class DCTradapp(tk.Tk):
    global cat_image_list
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.configure(background='SteelBlue3')
        self.title("Header DC trad")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        getCatCovers()
        getHeaderCovers()
        getUrls()
        # sidebar
        sidebar = tk.Frame(self, width=200, bg='SteelBlue4', height=500, relief='sunken', borderwidth=2)
        sidebar.pack(expand=False, fill='both', side='left', anchor='nw')


        button1 = tk.Button(sidebar, image=cat_image_list[0],
                            command=lambda: self.show_frame("DCRebirth"))
        button2 = tk.Button(sidebar, image=cat_image_list[1],
                            command=lambda: self.show_frame("DCPage"))
        button3 = tk.Button(sidebar, image=cat_image_list[2],
                            command=lambda: self.show_frame("Indes"))
        button4 = tk.Button(sidebar, image=cat_image_list[3],
                            command=lambda: self.show_frame("Marvel"))
        button5 = tk.Button(sidebar, text="Rafraîchir",
                            command=refresh())
        button1.pack()
        button2.pack()
        button3.pack()
        button4.pack()
        button5.pack(side='bottom')

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self, bg='SteelBlue3', width=400, height=500)
        container.pack(expand=True, fill='both', side='right', padx=20)
        #container.grid_rowconfigure(0, weight=1)
        #container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["DCRebirth"] = DCRebirth(parent=container, controller=self)
        self.frames["DCPage"] = DCPage(parent=container, controller=self)
        self.frames["Indes"] = Indes(parent=container, controller=self)
        self.frames["Marvel"] = Marvel(parent=container, controller=self)

        self.frames["DCRebirth"].grid(row=0, column=0, sticky="nsew")
        self.frames["DCPage"].grid(row=0, column=0, sticky="nsew")
        self.frames["Indes"].grid(row=0, column=0, sticky="nsew")
        self.frames["Marvel"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("DCRebirth")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class DCRebirth(tk.Frame):
    def __init__(self, parent, controller):
        global photo
        tk.Frame.__init__(self, parent)
        self.controller = controller
        coverA1 = tk.Button(self, image=photo[0], command= lambda: OpenUrl(urllist[0]))
        coverA1.grid(row=0, column=0)
        coverA2 = tk.Button(self, image=photo[1], command= lambda: OpenUrl(urllist[1]))
        coverA2.grid(row=0, column=1)
        coverA3 = tk.Button(self, image=photo[2], command= lambda: OpenUrl(urllist[2]))
        coverA3.grid(row=0, column=2)
        coverA4 = tk.Button(self, image=photo[3], command= lambda: OpenUrl(urllist[3]))
        coverA4.grid(row=1, column=0)
        coverA5 = tk.Button(self, image=photo[4], command= lambda: OpenUrl(urllist[4]))
        coverA5.grid(row=1, column=1)
        coverA6 = tk.Button(self, image=photo[5], command= lambda: OpenUrl(urllist[5]))
        coverA6.grid(row=1, column=2)
        coverA7 = tk.Button(self, image=photo[6], command= lambda: OpenUrl(urllist[6]))
        coverA7.grid(row=2, column=0)
        coverA8 = tk.Button(self, image=photo[7], command= lambda: OpenUrl(urllist[7]))
        coverA8.grid(row=2, column=1)
        coverA9 = tk.Button(self, image=photo[8], command= lambda: OpenUrl(urllist[8]))
        coverA9.grid(row=2, column=2)


class DCPage(tk.Frame):
    def __init__(self, parent, controller):
        global photo
        tk.Frame.__init__(self, parent)
        self.controller = controller
        coverA1 = tk.Button(self, image=photo[10], command= lambda: OpenUrl(urllist[10]))
        coverA1.grid(row=0, column=0)
        coverA2 = tk.Button(self, image=photo[11], command= lambda: OpenUrl(urllist[11]))
        coverA2.grid(row=0, column=1)
        coverA3 = tk.Button(self, image=photo[12], command= lambda: OpenUrl(urllist[12]))
        coverA3.grid(row=0, column=2)
        coverA4 = tk.Button(self, image=photo[13], command= lambda: OpenUrl(urllist[13]))
        coverA4.grid(row=1, column=0)
        coverA5 = tk.Button(self, image=photo[14], command= lambda: OpenUrl(urllist[14]))
        coverA5.grid(row=1, column=1)
        coverA6 = tk.Button(self, image=photo[15], command= lambda: OpenUrl(urllist[15]))
        coverA6.grid(row=1, column=2)
        coverA7 = tk.Button(self, image=photo[16], command= lambda: OpenUrl(urllist[16]))
        coverA7.grid(row=2, column=0)
        coverA8 = tk.Button(self, image=photo[17], command= lambda: OpenUrl(urllist[17]))
        coverA8.grid(row=2, column=1)
        coverA9 = tk.Button(self, image=photo[18], command= lambda: OpenUrl(urllist[18]))
        coverA9.grid(row=2, column=2)

class Indes(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        coverA1 = tk.Button(self, image=photo[20], command= lambda: OpenUrl(urllist[20]))
        coverA1.grid(row=0, column=0)
        coverA2 = tk.Button(self, image=photo[21], command= lambda: OpenUrl(urllist[21]))
        coverA2.grid(row=0, column=1)
        coverA3 = tk.Button(self, image=photo[22], command= lambda: OpenUrl(urllist[22]))
        coverA3.grid(row=0, column=2)
        coverA4 = tk.Button(self, image=photo[23], command= lambda: OpenUrl(urllist[23]))
        coverA4.grid(row=1, column=0)
        coverA5 = tk.Button(self, image=photo[24], command= lambda: OpenUrl(urllist[24]))
        coverA5.grid(row=1, column=1)
        coverA6 = tk.Button(self, image=photo[25], command= lambda: OpenUrl(urllist[25]))
        coverA6.grid(row=1, column=2)
        coverA7 = tk.Button(self, image=photo[26], command= lambda: OpenUrl(urllist[26]))
        coverA7.grid(row=2, column=0)
        coverA8 = tk.Button(self, image=photo[27], command= lambda: OpenUrl(urllist[27]))
        coverA8.grid(row=2, column=1)
        coverA9 = tk.Button(self, image=photo[28], command= lambda: OpenUrl(urllist[28]))
        coverA9.grid(row=2, column=2)

class Marvel(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        coverA1 = tk.Button(self, image=photo[30], command= lambda: OpenUrl(urllist[30]))
        coverA1.grid(row=0, column=0)
        coverA2 = tk.Button(self, image=photo[31], command= lambda: OpenUrl(urllist[31]))
        coverA2.grid(row=0, column=1)
        coverA3 = tk.Button(self, image=photo[32], command= lambda: OpenUrl(urllist[32]))
        coverA3.grid(row=0, column=2)
        coverA4 = tk.Button(self, image=photo[33], command= lambda: OpenUrl(urllist[33]))
        coverA4.grid(row=1, column=0)
        coverA5 = tk.Button(self, image=photo[34], command= lambda: OpenUrl(urllist[34]))
        coverA5.grid(row=1, column=1)
        coverA6 = tk.Button(self, image=photo[35], command= lambda: OpenUrl(urllist[35]))
        coverA6.grid(row=1, column=2)
        coverA7 = tk.Button(self, image=photo[36], command= lambda: OpenUrl(urllist[36]))
        coverA7.grid(row=2, column=0)
        coverA8 = tk.Button(self, image=photo[37], command= lambda: OpenUrl(urllist[37]))
        coverA8.grid(row=2, column=1)
        coverA9 = tk.Button(self, image=photo[38], command= lambda: OpenUrl(urllist[38]))
        coverA9.grid(row=2, column=2)


if __name__ == "__main__":
    app = DCTradapp()
    app.mainloop()
