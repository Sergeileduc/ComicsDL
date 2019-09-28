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
    def __init__(self, url, imageurl):
        self.url = url
        self.imageurl = imageurl

    def __str__(self):
        return f'{self.url} -- {self.imageurl}'

    def generate_tk_image(self):
        self.img = ImageTk.PhotoImage(image_from_url(self.imageurl))


class DCTradapp(tk.Tk):
    """My app with GUI."""

    global cat_image_list

    def __init__(self, *args, **kwargs):
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
        """Show a frame for the given page name"""
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
        images = []
        for i in self.headers:
            i.generate_tk_image()
        return images

    def _refresh(self):
        pass

    # Make images from covers
    def _get_cat_covers(self):
        # Catégories images
        # global cat_image_list
        image_list = []
        for cat in cat_img_urls:
            print(cat)
            image_list.append(ImageTk.PhotoImage(image_from_url(cat)))
        return image_list


class DCRebirth(tk.Frame):
    def __init__(self, parent, controller, headers):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[0].generate_tk_image()
        coverA1 = tk.Button(
                self, image=headers[0].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[0].url))
        coverA1.grid(row=0, column=0)
        headers[1].generate_tk_image()
        coverA2 = tk.Button(
                self, image=headers[1].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[1].url))
        coverA2.grid(row=0, column=1)
        headers[2].generate_tk_image()
        coverA3 = tk.Button(
                self, image=headers[2].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[2].url))
        coverA3.grid(row=0, column=2)
        headers[3].generate_tk_image()
        coverA4 = tk.Button(
                self, image=headers[3].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[3].url))
        coverA4.grid(row=1, column=0)
        headers[4].generate_tk_image()
        coverA5 = tk.Button(
                self, image=headers[4].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[4].url))
        coverA5.grid(row=1, column=1)
        headers[5].generate_tk_image()
        coverA6 = tk.Button(
                self, image=headers[5].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[5].url))
        coverA6.grid(row=1, column=2)
        headers[6].generate_tk_image()
        coverA7 = tk.Button(
                self, image=headers[6].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[6].url))
        coverA7.grid(row=2, column=0)
        headers[7].generate_tk_image()
        coverA8 = tk.Button(
                self, image=headers[7].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[7].url))
        coverA8.grid(row=2, column=1)
        headers[8].generate_tk_image()
        coverA9 = tk.Button(
                self, image=headers[8].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[8].url))
        coverA9.grid(row=2, column=2)


class DCPage(tk.Frame):
    def __init__(self, parent, controller, headers):
        global photo
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[10].generate_tk_image()
        coverA1 = tk.Button(
                self, image=headers[10].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[10].url))
        coverA1.grid(row=0, column=0)
        headers[11].generate_tk_image()
        coverA2 = tk.Button(
                self, image=headers[11].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[11].url))
        coverA2.grid(row=0, column=1)
        headers[12].generate_tk_image()
        coverA3 = tk.Button(
                self, image=headers[12].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[12].url))
        coverA3.grid(row=0, column=2)
        headers[13].generate_tk_image()
        coverA4 = tk.Button(
                self, image=headers[13].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[13].url))
        coverA4.grid(row=1, column=0)
        headers[14].generate_tk_image()
        coverA5 = tk.Button(
                self, image=headers[14].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[14].url))
        coverA5.grid(row=1, column=1)
        headers[15].generate_tk_image()
        coverA6 = tk.Button(
                self, image=headers[15].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[15].url))
        coverA6.grid(row=1, column=2)
        headers[16].generate_tk_image()
        coverA7 = tk.Button(
                self, image=headers[16].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[16].url))
        coverA7.grid(row=2, column=0)
        headers[17].generate_tk_image()
        coverA8 = tk.Button(
                self, image=headers[17].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[17].url))
        coverA8.grid(row=2, column=1)
        headers[18].generate_tk_image()
        coverA9 = tk.Button(
                self, image=headers[18].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[18].url))
        coverA9.grid(row=2, column=2)


class Indes(tk.Frame):

    def __init__(self, parent, controller, headers):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[20].generate_tk_image()
        coverA1 = tk.Button(
                self, image=headers[20].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[20].url))
        coverA1.grid(row=0, column=0)
        headers[21].generate_tk_image()
        coverA2 = tk.Button(
                self, image=headers[21].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[21].url))
        coverA2.grid(row=0, column=1)
        headers[22].generate_tk_image()
        coverA3 = tk.Button(
                self, image=headers[22].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[22].url))
        coverA3.grid(row=0, column=2)
        headers[23].generate_tk_image()
        coverA4 = tk.Button(
                self, image=headers[23].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[23].url))
        coverA4.grid(row=1, column=0)
        headers[24].generate_tk_image()
        coverA5 = tk.Button(
                self, image=headers[24].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[24].url))
        coverA5.grid(row=1, column=1)
        headers[25].generate_tk_image()
        coverA6 = tk.Button(
                self, image=headers[25].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[25].url))
        coverA6.grid(row=1, column=2)
        headers[26].generate_tk_image()
        coverA7 = tk.Button(
                self, image=headers[26].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[26].url))
        coverA7.grid(row=2, column=0)
        headers[27].generate_tk_image()
        coverA8 = tk.Button(
                self, image=headers[27].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[27].url))
        coverA8.grid(row=2, column=1)
        headers[28].generate_tk_image()
        coverA9 = tk.Button(
                self, image=headers[28].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[28].url))
        coverA9.grid(row=2, column=2)


class Marvel(tk.Frame):

    def __init__(self, parent, controller, headers):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        headers[30].generate_tk_image()
        coverA1 = tk.Button(
                self, image=headers[30].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[30].url))
        coverA1.grid(row=0, column=0)
        headers[31].generate_tk_image()
        coverA2 = tk.Button(
                self, image=headers[31].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[31].url))
        coverA2.grid(row=0, column=1)
        headers[32].generate_tk_image()
        coverA3 = tk.Button(
                self, image=headers[32].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[32].url))
        coverA3.grid(row=0, column=2)
        headers[33].generate_tk_image()
        coverA4 = tk.Button(
                self, image=headers[33].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[33].url))
        coverA4.grid(row=1, column=0)
        headers[34].generate_tk_image()
        coverA5 = tk.Button(
                self, image=headers[34].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[34].url))
        coverA5.grid(row=1, column=1)
        headers[35].generate_tk_image()
        coverA6 = tk.Button(
                self, image=headers[35].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[35].url))
        coverA6.grid(row=1, column=2)
        headers[36].generate_tk_image()
        coverA7 = tk.Button(
                self, image=headers[36].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[36].url))
        coverA7.grid(row=2, column=0)
        headers[37].generate_tk_image()
        coverA8 = tk.Button(
                self, image=headers[37].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[37].url))
        coverA8.grid(row=2, column=1)
        headers[38].generate_tk_image()
        coverA9 = tk.Button(
                self, image=headers[38].img, bg='SteelBlue3', relief='flat',
                command=lambda: open_url(headers[38].url))
        coverA9.grid(row=2, column=2)


if __name__ == "__main__":
    app = DCTradapp()
    app.mainloop()
