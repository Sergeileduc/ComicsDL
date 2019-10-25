#!/usr/bin/python3
# -*-coding:utf-8 -*
"""Little app to display DCtrad header."""

# import io
import io
import requests
from PIL import Image, ImageTk  # pip install pillow
import tkinter as tk
from tkinter import font as tkfont  # python 3
from bs4 import BeautifulSoup
import webbrowser
from urllib.parse import urljoin

dctrad_base = 'http://www.dctrad.fr'
dctradpage = 'http://www.dctrad.fr/index.php'
cat_img_urls = [
    'http://www.dctrad.fr/images/icons/forum/RebirthK.png',
    'http://www.dctrad.fr//images/icons/forum/dccomicsv2.png',
    'http://www.dctrad.fr//images/icons/forum/IconindiedctK.png',
    'http://www.dctrad.fr/images/icons/forum/MarvelK.png']
refresh_logo_url = 'http://icons.iconarchive.com/icons/graphicloads/' \
                    '100-flat-2/128/arrow-refresh-4-icon.png'


def image_from_url(url):
    """Get image from url."""
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


def open_url(url):
    """Open url."""
    # webbrowser.open_new(url)
    webbrowser.open(url, new=0, autoraise=False)
    return


# Get html from url
def _return_html(url):
    hdr = {'Accept': 'text/html', 'User-Agent': "Fiddler"}
    # req = urllib2.Request(url, headers=hdr)
    try:
        html = requests.get(url, headers=hdr).text
        return html
    except requests.exceptions.HTTPError as e:
        print(e)


def _return_soup(url):
    """Get soup from url."""
    return BeautifulSoup(_return_html(url), 'html.parser')


class HeaderPic:
    """Class to build header object with url and image url."""

    def __init__(self, url, imageurl):
        """Init with topic url and image url."""
        self.url = url
        self.imageurl = imageurl

    def __str__(self):
        """Str with topic url and image url."""
        return f'{self.url} -- {self.imageurl}'

    def generate_tk_image(self):
        """Generate Tk PhotoImage from image url."""
        self.img = ImageTk.PhotoImage(image_from_url(self.imageurl))


class DCTradapp(tk.Tk):
    """My app with GUI."""

    def __init__(self, *args, **kwargs):
        """Init Tkinter GUI application."""
        logo = False
        self.headers = self._make_header_list(dctradpage)

        tk.Tk.__init__(self, *args, **kwargs)
        self.configure(background='SteelBlue3')
        self.title("Header DC trad")
        self.title_font = tkfont.Font(
                family='Helvetica', size=18, weight="bold", slant="italic")
        self.cat_image_list = self._get_cat_covers()

        try:
            self.cat_image_list.append(
                    ImageTk.PhotoImage(image_from_url(refresh_logo_url)))
            logo = True
        except Exception:
            logo = False

        sidebar = tk.Frame(self, width=200, bg='SteelBlue4',
                           height=500, relief='groove', borderwidth=1)
        sidebar.pack(expand=False, fill='both', side='left', anchor='nw')

        button1 = tk.Button(sidebar, image=self.cat_image_list[0],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("DCRebirth"))
        button2 = tk.Button(sidebar, image=self.cat_image_list[1],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("DCPage"))
        button3 = tk.Button(sidebar, image=self.cat_image_list[2],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("Indes"))
        button4 = tk.Button(sidebar, image=self.cat_image_list[3],
                            bg='SteelBlue4', relief='flat',
                            command=lambda: self.show_frame("Marvel"))
        if logo:
            button5 = tk.Button(sidebar, image=self.cat_image_list[4],
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

        self.frames = {"DCRebirth": DCRebirth(parent=container,
                                              controller=self,
                                              headers=self.headers),
                       "DCPage": DCPage(parent=container,
                                        controller=self,
                                        headers=self.headers),
                       "Indes": Indes(parent=container,
                                      controller=self,
                                      headers=self.headers),
                       "Marvel": Marvel(parent=container,
                                        controller=self,
                                        headers=self.headers)}

        self.frames["DCRebirth"].grid(row=0, column=0, sticky="nsew")
        self.frames["DCPage"].grid(row=0, column=0, sticky="nsew")
        self.frames["Indes"].grid(row=0, column=0, sticky="nsew")
        self.frames["Marvel"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("DCRebirth")

    def show_frame(self, page_name):
        """Show a frame for the given page name."""
        frame = self.frames[page_name]
        frame.tkraise()

    # make list of headerPic objects:
    def _make_header_list(self, dctradurl):
        # global headers
        headers = []
        my_list = _return_soup(dctradpage).select('span.btn-cover a')
        # list = _return_soup(dctradpage).find_all('span', class_="btn-cover")
        for l in my_list:
            url = l['href']
            imgurl = urljoin(dctrad_base, l.img['src'])
            headerpic = HeaderPic(url, imgurl)
            headers.append(headerpic)
        return headers

    def _generate_images(self):
        for i in self.headers:
            i.generate_tk_image()

    def _refresh(self):
        pass

    # Make images from covers
    def _get_cat_covers(self):
        image_list = [ImageTk.PhotoImage(image_from_url(c))
                      for c in cat_img_urls]
        return image_list


class DCRebirth(tk.Frame):
    """Tk frame DC Rebirth."""

    def __init__(self, parent, controller, headers):
        """Init frame."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        for index, header in enumerate(headers[:9]):
            i, j = divmod(index, 3)
            header.generate_tk_image()
            btn = tk.Button(
                self, image=header.img, bg='SteelBlue3', relief='flat',
                command=lambda url=header.url: open_url(url))
            btn.grid(row=i, column=j)


class DCPage(tk.Frame):
    """Tk frame DC."""

    def __init__(self, parent, controller, headers):
        """Init frame."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        for index, header in enumerate(headers[10:19]):
            i, j = divmod(index, 3)
            header.generate_tk_image()
            btn = tk.Button(
                self, image=header.img, bg='SteelBlue3', relief='flat',
                command=lambda url=header.url: open_url(url))
            btn.grid(row=i, column=j)


class Indes(tk.Frame):
    """Tk frame DC Indies."""

    def __init__(self, parent, controller, headers):
        """Init frame."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        for index, header in enumerate(headers[20:29]):
            i, j = divmod(index, 3)
            header.generate_tk_image()
            btn = tk.Button(
                self, image=header.img, bg='SteelBlue3', relief='flat',
                command=lambda url=header.url: open_url(url))
            btn.grid(row=i, column=j)


class Marvel(tk.Frame):
    """Tk frame Marvel."""

    def __init__(self, parent, controller, headers):
        """Init frame."""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        for index, header in enumerate(headers[30:39]):
            i, j = divmod(index, 3)
            header.generate_tk_image()
            btn = tk.Button(
                self, image=header.img, bg='SteelBlue3', relief='flat',
                command=lambda url=header.url: open_url(url))
            btn.grid(row=i, column=j)


if __name__ == "__main__":
    app = DCTradapp()
    app.mainloop()
