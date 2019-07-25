#!/usr/bin/python3
# -*-coding:utf-8 -*
# import io
import io
import requests
from PIL import Image, ImageTk  # pip install pillow
import tkinter as tk
from tkinter import font as tkfont  # python 3
from bs4 import BeautifulSoup
import webbrowser

dctradpage = 'http://www.dctrad.fr/index.php'
cat_img_urls = [
    'http://www.dctrad.fr/images/icons/forum/RebirthK.png',
    'http://www.dctrad.fr//images/icons/forum/dccomicsv2.png',
    'http://www.dctrad.fr//images/icons/forum/IconindiedctK.png',
    'http://www.dctrad.fr/images/icons/forum/MarvelK.png']
refresh_logo_url = 'http://icons.iconarchive.com/icons/graphicloads/' \
                    '100-flat-2/128/arrow-refresh-4-icon.png'
# shared lists
# urllist = list()
# photo = list()
# headers = list()
cat_image_list = list()


# image from url
def imagefromurl(url):
    try:
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        return img
    except requests.exceptions.HTTPError as e:
        print(e)
        return
    except IOError as e:
        print(e)
        return


# Open url
def OpenUrl(url):
    # webbrowser.open_new(url)
    webbrowser.open(url, new=0, autoraise=False)
    return


# Get html from url
def _returnHTML(url):
    hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    # req = urllib2.Request(url, headers=hdr)
    try:
        html = requests.get(url, headers=hdr).text
        return html
    except requests.exceptions.HTTPError as e:
        print(e)


# Get soup from url
def _returnSoup(url):
    return BeautifulSoup(_returnHTML(url), 'html.parser')


# Make images from covers
def getCatCovers():
    # Catégories images
    global cat_image_list
    del cat_image_list[:]
    for cat in cat_img_urls:
        cat_image_list.append(ImageTk.PhotoImage(imagefromurl(cat)))
    return cat_image_list


# Get publication posts urls
# def getUrls(comicslist):
#     global urllist
#     del urllist[:]
#     for a in comicslist:
#         if a.has_attr('href'):
#             urllist.append(a['href'])
#     return


class HeaderPic:
    def __init__(self, url, imageurl):
        self.url = url
        self.imageurl = imageurl

    def __str__(self):
        return f'{self.url} -- {self.imageurl}'

    def _generateTKimage(self):
        self.img = ImageTk.PhotoImage(imagefromurl(self.imageurl))


class DCTradapp(tk.Tk):
    global cat_image_list

    def __init__(self, *args, **kwargs):
        logo = False
        # soup = _returnSoup(dctradpage)
        # headerlist = soup.find_all('span', class_="btn-cover")
        # comicslist = _returnSoup(dctradpage).select('span.btn-cover a')
        self.headers = self._makeHeaderList(dctradpage)
        # coverlist = soup.select('span.btn-cover img')

        tk.Tk.__init__(self, *args, **kwargs)
        self.configure(background='SteelBlue3')
        self.title("Header DC trad")
        self.title_font = tkfont.Font(
                family='Helvetica', size=18, weight="bold", slant="italic")
        cat_image_list = getCatCovers()
        # self.photos = self._generate_images()
        # self.headers[0]._generateTKimage()
        # getHeaderCovers()
        # refresh(comicslist)
        # sidebar
        try:
            cat_image_list.append(
                    ImageTk.PhotoImage(imagefromurl(refresh_logo_url)))
            logo = True
        except Exception:
            logo = False

        sidebar = tk.Frame(self, width=200, bg='SteelBlue4',
                           height=500, relief='groove', borderwidth=1)
        sidebar.pack(expand=False, fill='both', side='left', anchor='nw')

        button1 = tk.Button(sidebar, image=cat_image_list[0],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("DCRebirth"))
        button2 = tk.Button(sidebar, image=cat_image_list[1],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("DCPage"))
        button3 = tk.Button(sidebar, image=cat_image_list[2],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("Indes"))
        button4 = tk.Button(sidebar, image=cat_image_list[3],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("Marvel"))
        if logo:
            button5 = tk.Button(sidebar, image=cat_image_list[4],
                                bg='SteelBlue4', relief='flat',
                                command=self._refresh())
        else:
            button5 = tk.Button(sidebar, text="Rafraîchir",
                                command=self._refresh())

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
        # container.grid_rowconfigure(0, weight=1)
        # container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames["DCRebirth"] = DCRebirth(parent=container,
                                             controller=self,
                                             headers=self.headers)
        self.frames["DCPage"] = DCPage(parent=container,
                                       controller=self,
                                       headers=self.headers)
        self.frames["Indes"] = Indes(parent=container,
                                     controller=self,
                                     headers=self.headers)
        self.frames["Marvel"] = Marvel(parent=container,
                                       controller=self,
                                       headers=self.headers)

        self.frames["DCRebirth"].grid(row=0, column=0, sticky="nsew")
        self.frames["DCPage"].grid(row=0, column=0, sticky="nsew")
        self.frames["Indes"].grid(row=0, column=0, sticky="nsew")
        self.frames["Marvel"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("DCRebirth")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    # make list of headerPic objects:
    def _makeHeaderList(self, dctradurl):
        # global headers
        headers = []
        list = _returnSoup(dctradpage).select('span.btn-cover a')
        # list = _returnSoup(dctradpage).find_all('span', class_="btn-cover")
        for l in list:
            url = l['href']
            imgurl = l.img['src']
            headerpic = HeaderPic(url, imgurl)
            headers.append(headerpic)
        return headers

    def _generate_images(self):
        images = []
        for i in self.headers:
            i._generateTKimage()
        return images

    def _refresh(self):
        pass


class DCRebirth(tk.Frame):
    def __init__(self, parent, controller, headers):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[0]._generateTKimage()
        coverA1 = tk.Button(
                self, image=headers[0].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[0].url))
        coverA1.grid(row=0, column=0)
        headers[1]._generateTKimage()
        coverA2 = tk.Button(
                self, image=headers[1].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[1].url))
        coverA2.grid(row=0, column=1)
        headers[2]._generateTKimage()
        coverA3 = tk.Button(
                self, image=headers[2].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[2].url))
        coverA3.grid(row=0, column=2)
        headers[3]._generateTKimage()
        coverA4 = tk.Button(
                self, image=headers[3].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[3].url))
        coverA4.grid(row=1, column=0)
        headers[4]._generateTKimage()
        coverA5 = tk.Button(
                self, image=headers[4].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[4].url))
        coverA5.grid(row=1, column=1)
        headers[5]._generateTKimage()
        coverA6 = tk.Button(
                self, image=headers[5].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[5].url))
        coverA6.grid(row=1, column=2)
        headers[6]._generateTKimage()
        coverA7 = tk.Button(
                self, image=headers[6].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[6].url))
        coverA7.grid(row=2, column=0)
        headers[7]._generateTKimage()
        coverA8 = tk.Button(
                self, image=headers[7].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[7].url))
        coverA8.grid(row=2, column=1)
        headers[8]._generateTKimage()
        coverA9 = tk.Button(
                self, image=headers[8].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[8].url))
        coverA9.grid(row=2, column=2)


class DCPage(tk.Frame):
    def __init__(self, parent, controller, headers):
        global photo
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[10]._generateTKimage()
        coverA1 = tk.Button(
                self, image=headers[10].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[10].url))
        coverA1.grid(row=0, column=0)
        headers[11]._generateTKimage()
        coverA2 = tk.Button(
                self, image=headers[11].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[11].url))
        coverA2.grid(row=0, column=1)
        headers[12]._generateTKimage()
        coverA3 = tk.Button(
                self, image=headers[12].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[12].url))
        coverA3.grid(row=0, column=2)
        headers[13]._generateTKimage()
        coverA4 = tk.Button(
                self, image=headers[13].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[13].url))
        coverA4.grid(row=1, column=0)
        headers[14]._generateTKimage()
        coverA5 = tk.Button(
                self, image=headers[14].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[14].url))
        coverA5.grid(row=1, column=1)
        headers[15]._generateTKimage()
        coverA6 = tk.Button(
                self, image=headers[15].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[15].url))
        coverA6.grid(row=1, column=2)
        headers[16]._generateTKimage()
        coverA7 = tk.Button(
                self, image=headers[16].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[16].url))
        coverA7.grid(row=2, column=0)
        headers[17]._generateTKimage()
        coverA8 = tk.Button(
                self, image=headers[17].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[17].url))
        coverA8.grid(row=2, column=1)
        headers[18]._generateTKimage()
        coverA9 = tk.Button(
                self, image=headers[18].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[18].url))
        coverA9.grid(row=2, column=2)


class Indes(tk.Frame):

    def __init__(self, parent, controller, headers):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[20]._generateTKimage()
        coverA1 = tk.Button(
                self, image=headers[20].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[20].url))
        coverA1.grid(row=0, column=0)
        headers[21]._generateTKimage()
        coverA2 = tk.Button(
                self, image=headers[21].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[21].url))
        coverA2.grid(row=0, column=1)
        headers[22]._generateTKimage()
        coverA3 = tk.Button(
                self, image=headers[22].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[22].url))
        coverA3.grid(row=0, column=2)
        headers[23]._generateTKimage()
        coverA4 = tk.Button(
                self, image=headers[23].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[23].url))
        coverA4.grid(row=1, column=0)
        headers[24]._generateTKimage()
        coverA5 = tk.Button(
                self, image=headers[24].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[24].url))
        coverA5.grid(row=1, column=1)
        headers[25]._generateTKimage()
        coverA6 = tk.Button(
                self, image=headers[25].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[25].url))
        coverA6.grid(row=1, column=2)
        headers[26]._generateTKimage()
        coverA7 = tk.Button(
                self, image=headers[26].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[26].url))
        coverA7.grid(row=2, column=0)
        headers[27]._generateTKimage()
        coverA8 = tk.Button(
                self, image=headers[27].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[27].url))
        coverA8.grid(row=2, column=1)
        headers[28]._generateTKimage()
        coverA9 = tk.Button(
                self, image=headers[28].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[28].url))
        coverA9.grid(row=2, column=2)


class Marvel(tk.Frame):

    def __init__(self, parent, controller, headers):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[30]._generateTKimage()
        coverA1 = tk.Button(
                self, image=headers[30].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[30].url))
        coverA1.grid(row=0, column=0)
        headers[31]._generateTKimage()
        coverA2 = tk.Button(
                self, image=headers[31].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[31].url))
        coverA2.grid(row=0, column=1)
        headers[32]._generateTKimage()
        coverA3 = tk.Button(
                self, image=headers[32].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[32].url))
        coverA3.grid(row=0, column=2)
        headers[33]._generateTKimage()
        coverA4 = tk.Button(
                self, image=headers[33].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[33].url))
        coverA4.grid(row=1, column=0)
        headers[34]._generateTKimage()
        coverA5 = tk.Button(
                self, image=headers[34].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[34].url))
        coverA5.grid(row=1, column=1)
        headers[35]._generateTKimage()
        coverA6 = tk.Button(
                self, image=headers[35].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[35].url))
        coverA6.grid(row=1, column=2)
        headers[36]._generateTKimage()
        coverA7 = tk.Button(
                self, image=headers[36].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[36].url))
        coverA7.grid(row=2, column=0)
        headers[37]._generateTKimage()
        coverA8 = tk.Button(
                self, image=headers[37].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[37].url))
        coverA8.grid(row=2, column=1)
        headers[38]._generateTKimage()
        coverA9 = tk.Button(
                self, image=headers[38].img, bg='SteelBlue3', relief='flat',
                command=lambda: OpenUrl(headers[38].url))
        coverA9.grid(row=2, column=2)


if __name__ == "__main__":
    app = DCTradapp()
    app.mainloop()
