#!/usr/bin/python3
# -*-coding:utf-8 -*
"""Little app to display DCtrad header."""

import tkinter as tk
import webbrowser
from tkinter import font as tkfont  # python 3
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk  # pip install pillow

DCTRAD_BASE = 'https://www.dctrad.fr'
DCTRAD_PAGE = f'{DCTRAD_BASE}/index.php'
cat_img_urls = [
    'https://www.dctrad.fr/images/icons/forum/RebirthK.png',
    'https://www.dctrad.fr//images/icons/forum/dccomicsv2.png',
    'https://www.dctrad.fr//images/icons/forum/IconindiedctK.png',
    'https://www.dctrad.fr/images/icons/forum/MarvelK.png']
REFRESH_LOGO_URL = 'http://icons.iconarchive.com/icons/graphicloads/' \
                   '100-flat-2/128/arrow-refresh-4-icon.png'


class HeaderPic:
    """Class to build header object with url and image url."""

    def __init__(self, url, imageurl):
        """Init with topic url and image url."""
        self.url = url
        self.imageurl = imageurl
        self.img = None

    def __str__(self) -> str:
        """Str with topic url and image url."""
        return f'{self.url} -- {self.imageurl}'

    def generate_tk_image(self):
        """Generate Tk PhotoImage from image url."""
        self.img = ImageTk.PhotoImage(image_from_url(self.imageurl))


def image_from_url(url: str) -> Image:
    """Get image from url.

    Args:
        url (str): url of remote image

    Returns:
        Image: _description_
    """
    try:
        return Image.open(requests.get(url, stream=True).raw)
    except requests.exceptions.HTTPError as e:
        print(e)
    except IOError as e:
        print(e)


def open_url(url: str):
    """Open url."""
    # webbrowser.open_new(url)
    webbrowser.open(url, new=0, autoraise=False)


# Get html from url
def _return_html(url: str) -> str:
    """Return HTML string.

    Args:
        url (str): url

    Returns:
        str: html
    """
    # hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    # req = urllib2.Request(url, headers=hdr)
    try:
        return requests.get(url).text
    except requests.exceptions.HTTPError as e:
        print(e)


def _return_soup(url: str) -> BeautifulSoup:
    """Get soup from url."""
    return BeautifulSoup(_return_html(url), 'html.parser')


def _make_header_list() -> list[HeaderPic]:
    """Return list of headerPic objects."""
    headers = []
    my_list = _return_soup(DCTRAD_PAGE).select('span.btn-cover a')
    for i in my_list:
        url = i['href']
        imgurl = urljoin(DCTRAD_BASE, i.img['src'])
        headerpic = HeaderPic(url, imgurl)
        headers.append(headerpic)
    return headers


class DCTradapp(tk.Tk):
    """My app with GUI."""

    def __init__(self, *args, **kwargs):
        """Init Tkinter GUI application."""
        super().__init__(*args, **kwargs)
        self.logo: bool = False
        self.headers: list[HeaderPic] = _make_header_list()
        self.configure(background='SteelBlue3')
        self.title("Header DC trad")
        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")
        self.cat_image_list = self._get_cat_covers()

        try:
            self.cat_image_list.append(ImageTk.PhotoImage(image_from_url(REFRESH_LOGO_URL)))
            self.logo = True
        except Exception:
            self.logo = False

        sidebar = tk.Frame(self, width=200, bg='SteelBlue4',
                           height=500, relief='groove', borderwidth=1)
        sidebar.pack(expand=False, fill='both', side='left', anchor='nw')

        cat_list = ["DCRebirth", "DCPage", "Indes", "Marvel"]

        # Create cat buttons
        for i in range(len(cat_list)):
            btn = tk.Button(sidebar, image=self.cat_image_list[i],
                            bg='SteelBlue4', relief='flat',
                            command=lambda x=cat_list[i]: self.show_frame(x))
            btn.pack()

        # Refresh button
        if self.logo:
            button5 = tk.Button(sidebar, image=self.cat_image_list[4],
                                bg='SteelBlue4', relief='flat',
                                command=self._refresh)
        else:
            button5 = tk.Button(sidebar, text="Rafraîchir",
                                command=self._refresh)
        button5.pack(side='bottom')

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self, bg='SteelBlue3', width=400, height=500)
        container.pack(expand=True, fill='both', side='right', padx=20)
        # container.grid_rowconfigure(0, weight=1)
        # container.grid_columnconfigure(0, weight=1)

        self.frames = {"DCRebirth": HeaderGrid(parent=container,
                                               controller=self,
                                               headers=self.headers,
                                               start=0),
                       "DCPage": HeaderGrid(parent=container,
                                            controller=self,
                                            headers=self.headers,
                                            start=10),
                       "Indes": HeaderGrid(parent=container,
                                           controller=self,
                                           headers=self.headers,
                                           start=20),
                       "Marvel": HeaderGrid(parent=container,
                                            controller=self,
                                            headers=self.headers,
                                            start=30)}

        self.frames["DCRebirth"].grid(row=0, column=0, sticky="nsew")
        self.frames["DCPage"].grid(row=0, column=0, sticky="nsew")
        self.frames["Indes"].grid(row=0, column=0, sticky="nsew")
        self.frames["Marvel"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("DCRebirth")

    def show_frame(self, page_name: str):
        """Show a frame for the given page name.

        Args:
            page_name (str): key of the frame ('DCRebirth', 'Marvel', etc...)
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def _refresh(self):
        print("refresh complete")

    # Make images from covers
    def _get_cat_covers(self):
        return [ImageTk.PhotoImage(image_from_url(c)) for c in cat_img_urls]


class HeaderGrid(tk.Frame):
    """Tk frame for 3x3 header grid.

    start is the start index in the headers list.
    """

    def __init__(self, parent, controller, headers: list[HeaderPic], start=0):
        """Init frame."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        for index, header in enumerate(headers[start:start + 9]):
            i, j = divmod(index, 3)
            header.generate_tk_image()
            btn = tk.Button(self, image=header.img, bg='SteelBlue3', relief='flat',
                            command=lambda url=header.url: open_url(url))
            btn.grid(row=i, column=j)


if __name__ == "__main__":
    app = DCTradapp()
    app.mainloop()
