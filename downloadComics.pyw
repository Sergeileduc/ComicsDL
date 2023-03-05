#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""GUI to download comics on getcomics.info."""

import requests
import sys
import threading
import urllib.request
import urllib.error

import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from utils import getcomics
from utils.getcomics import (find_buttons, find_zippy_button,
                             getresults, ZippyButtonError)

from utils.std_redirect import StdRedirector
from utils.tools import convert2bytes, bytes_2_human_readable
from utils.urltools import getfinalurl
from utils.zpshare import (check_url, DownloadButtonError,
                           find_zippy_download_button, get_file_url)


# Main program interface and code
class Getcomics(tk.Tk):
    """GUI made with tk.TK."""

    deep_bg = '#263238'
    fg = 'white'
    button_dark = '#546E7A'
    dark2 = '#37474F'
    color1 = '#37474F'
    # color2='#455A64'
    dark3 = '#455A64'
    gray98 = '#FAFAFA'

    title_string = "Télécharger sur Getcomics V2019-07"

    def __init__(self):
        """Init Tkinter program with GUI."""
        def my_function(event):
            dl_canvas.configure(
                scrollregion=dl_canvas.bbox("all"), width=200, height=200)
        super().__init__()
        size_x = 800  # width
        size_y = 600  # height

        # Gets both half the screen width/height and window width/height
        pos_x = int(self.winfo_screenwidth() / 2 - size_x / 2)
        pos_y = int(self.winfo_screenheight() / 2 - size_y / 2)

        self.result_width = 50
        self.dl_width = 40

        style = ttk.Style()
        style.configure("deepBG.TFrame",
                        foreground=self.fg,
                        background=self.deep_bg,
                        border=0, relief='flat')
        style.configure("dark1.TFrame",
                        foreground=self.fg, background=self.color1,
                        border=0, relief='flat', highlightthickness=0)
        style.configure("L.TLabel",
                        foreground=self.fg, background=self.color1,
                        relief='raised', font=("Verdana", 12))
        style.configure('pages.TButton', font=("Verdana", 12), relief='raised',
                        background=self.dark3, foreground=self.fg,
                        border=2, highlightthickness=0)
        style.map('pages.TButton',
                  foreground=[('active', 'black')],
                  background=[('active', self.fg)])
        style.configure('dl.TButton',
                        background=self.color1, foreground=self.fg,
                        highlightthickness=0, font=("Verdana", 12, 'bold'))
        style.map('dl.TButton',
                  foreground=[('active', 'black')],
                  background=[('active', self.fg)])

        self.page = 1
        self.current_percent = tk.IntVar()
        self.current_percent.set(0)
        self.percent = tk.IntVar()
        self.dl_bytes = tk.IntVar()
        self.percent.set(0)
        self.dl_bytes.set(0)
        self.max_percent = 100
        self.list_size = 0
        self.choices = ['Recherche par TAG', 'Recherche simple']
        self.mode = tk.StringVar()
        self.mode.set('Recherche simple')
        self.user_search = tk.StringVar()
        self.button_list = list()
        self.search_list = list()
        self.download_list = list()
        self.my_list = list()
        self.wm_geometry(f"{size_x}x{size_y}+{pos_x}+{pos_y}")
        self.title(self.title_string)
        self.configure(background=self.deep_bg)

        top_bar = ttk.Frame(self, style="deepBG.TFrame")
        mainframe = ttk.Frame(self, style="deepBG.TFrame")
        self.results_frame = ttk.Frame(mainframe, style="dark1.TFrame")
        right_frame = ttk.Frame(mainframe, style="dark1.TFrame")
        button_bar = ttk.Frame(self.results_frame, style="deepBG.TFrame")

        bottom_bar = ttk.Frame(self, style="deepBG.TFrame")
        self.prev_page = ttk.Button(button_bar,
                                    text="page précédente",
                                    style="pages.TButton",
                                    command=self.go_to_prev_page)
        next_page = ttk.Button(button_bar,
                               text="page suivante",
                               style="pages.TButton",
                               command=self.go_to_next_page)
        # messageRecherche = tk.Label(
        #         top_bar, text="Rechercher sur Getcomics",
        #         bg=self.dark2, fg=self.fg,
        #         justify=tk.CENTER, font=("Helvetica", 12))
        choice = tk.OptionMenu(top_bar, self.mode, *self.choices)
        choice.config(bg=self.dark3, fg=self.fg, relief='flat',
                      border=0, highlightthickness=0)
        choice["menu"].config(bg=self.dark3, fg=self.fg,
                              relief='flat', border=0)
        search = tk.Entry(top_bar, width=self.result_width, justify='center',
                          insertbackground=self.fg,
                          bg=self.dark2, fg=self.fg,
                          textvariable=self.user_search,
                          font=("Verdana", 12))

        dl_canvas = tk.Canvas(right_frame,
                              bg=self.color1,
                              highlightthickness=0)
        self.dl_frame = ttk.Frame(dl_canvas,
                                  style="dark1.TFrame")
        scrollbar = ttk.Scrollbar(dl_canvas,
                                  orient="vertical",
                                  command=dl_canvas.yview)
        instructions = ttk.Label(self.results_frame, style="L.TLabel",
                                 text='Cliquez pour ajouter un élément '
                                 'à votre liste de téléchargement')
        liste = tk.Label(right_frame, width=self.dl_width,
                         bg=self.dark2, fg=self.fg,
                         relief='raised', text="Liste de téléchargement",
                         font=("Verdana", 12))
        dl_all = ttk.Button(right_frame, text="Télécharger la liste",
                            style="dl.TButton",
                            command=lambda: self.dl_com(self.download_list))

        output_text = tkst.ScrolledText(bottom_bar, height=8, bg='black',
                                        fg='white', wrap=tk.WORD)
        self.progress = ttk.Progressbar(bottom_bar, orient="horizontal",
                                        variable=self.current_percent,
                                        mode="determinate")
        self.progress2 = ttk.Progressbar(bottom_bar, orient="horizontal",
                                         variable=self.percent,
                                         mode="determinate")

        top_bar.pack(fill='x', anchor='n', padx=20, pady=20)
        mainframe.pack(fill='both', expand=1, anchor='nw',
                       padx=20, pady=(0, 5))
        self.results_frame.pack(side='left', anchor='nw', fill='both',
                                expand=1, padx=(0, 20))
        right_frame.pack(side='left', anchor='ne', fill='y', expand=1)
        button_bar.pack(side='bottom', anchor='sw', fill='x', expand=1)

        next_page.pack(side='right', padx=(0, 50))
        search.pack(side='left')
        choice.pack(side='right')
        search.focus_set()
        search.bind("<Return>", self.search_comics)
        instructions.pack(fill='x')
        liste.pack(fill='x')
        dl_canvas.pack(fill='both', expand=1)
        scrollbar.pack(side='right', fill='y')
        dl_canvas.configure(yscrollcommand=scrollbar.set)
        dl_canvas.create_window((0, 0), window=self.dl_frame, anchor='nw')
        self.dl_frame.bind("<Configure>", my_function)
        dl_all.pack(fill='x', side='bottom')

        bottom_bar.pack(fill='x')
        self.progress.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.progress2.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        output_text.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        sys.stdout = StdRedirector(output_text)

        self.search_comics(None)

    @staticmethod
    def destroy_list(widget_list):
        """Destroy a list of widgets (like buttons)."""
        for w in widget_list:
            w.destroy()
        widget_list.clear()
        pass

    # Search comics function
    def search_comics(self, event):
        """Search comic on getcomics.info."""
        self.search_list.clear()
        self.destroy_list(self.button_list)
        search_mode = self.choices.index(self.mode.get())
        self.search_list = getresults(
            getcomics.searchurl(self.user_search.get(), search_mode, self.page)
            )
        # button_list = list()
        for i in self.search_list:
            title = f'{i["title"]} ({i["size"]})'
            new_button = tk.Button(
                self.results_frame, text=title, width=self.result_width,
                relief='flat', border=0,
                bg=self.button_dark, fg=self.fg,
                activebackground=self.gray98, activeforeground='black',
                highlightthickness=0, font=("Verdana", 10)
                )
            new_button.config(
                command=lambda button=new_button: self.add_to_dl(button))
            new_button.pack(fill='both', expand=1, pady=0)
            self.button_list.append(new_button)
        return

    def dl_com(self, liste):
        """Download one comic."""
        try:
            thread1 = threading.Thread(target=self.down_all_com, args=[liste])
            thread1.start()
        except Exception as e:
            print(e)
            pass

    def add_to_dl(self, button):
        """Click to add to DL list."""
        index = self.button_list.index(button)
        comic = button.cget('text')
        if comic not in (item["title"] for item in self.download_list):
            if self.search_list[index]["size"] is not None:
                size_bytes = convert2bytes(self.search_list[index]["size"])
                self.list_size += size_bytes
            new_dl = tk.Button(self.dl_frame, text=button.cget('text').title(),
                               width=self.result_width, anchor='w',
                               bg=self.button_dark, fg=self.fg,
                               activebackground=self.gray98,
                               activeforeground='black',
                               relief='flat', border=0, highlightthickness=0,
                               font=("Verdana", 10))
            new_dl.config(command=lambda button=new_dl: self.remove_dl(button))
            new_dl.pack(fill='both', expand=1, pady=0)
            self.download_list.append(
                {"url": self.search_list[index]["url"],
                 "title": self.search_list[index]["title"],
                 "button": new_dl,
                 "size": self.search_list[index]["size"]})
            total_size = bytes_2_human_readable(self.list_size)
            print(f"Taille de la file d'attente (donnée indicative) : "
                  f"{total_size}")
        else:
            print("Already in your DL list")

    def remove_dl(self, button):
        """Click to remove an item function."""
        for i in self.download_list:
            if button == i["button"]:
                if i["size"] is not None:
                    bytes = convert2bytes(i["size"])
                    self.list_size -= bytes
                self.download_list.remove(i)
        button.destroy()
        total_size = bytes_2_human_readable(self.list_size)
        print(f"Taille de la file d'attente (donnée indicative) : "
              f"{total_size}")

    def down_all_com(self, liste):
        """Download all comics in the list."""
        self.dl_bytes.set(0)
        for dl in liste:
            try:
                self.down_com(dl["url"])
            except Exception as e:
                print(e)
                print("Something went wrong")
        print("Terminé, vous pouvez quitter")
        return

    def down_com(self, url):
        """Find Zippyshare Button, find download url, download."""
        final_url = getfinalurl(url)
        print("Trying " + final_url)
        try:
            buttons = find_buttons(final_url)
            zippylink = find_zippy_button(buttons)
            finalzippy = check_url(zippylink)
        except ZippyButtonError as e:
            print(e)
            return
        except urllib.error.HTTPError as e:
            print("down_com got HTTPError")
            print(e)
            raise
        try:
            print(finalzippy)
            self.down_com_zippy(finalzippy)
        except Exception as e:
            print(e)
            print("error in down_com_zippy")
        return

    def down_com_zippy(self, url):
        """Download from zippyshare."""
        self.progress["value"] = 0
        try:
            down_button = find_zippy_download_button(url)
        except DownloadButtonError as e:
            print(e)
            return
        try:
            full_url, filename = get_file_url(url, down_button)
            print("Download from zippyshare into : " + filename)
            r = requests.get(full_url, stream=True)
            size = int(r.headers['Content-length'])  # Size in bytes
            print(bytes_2_human_readable(size))
        except Exception as e:
            size = 0
            print(e)
            print("Can't get download link on zippyshare page")

        # Download from url & trim it a little bit
        with open(filename, 'wb') as f:
            try:
                dl = 0
                if self.list_size == 0:
                    self.list_size = 1
                for block in r.iter_content(51200):
                    dl += len(block)
                    self.current_percent.set(int(100 * dl / size))
                    self.dl_bytes.set(self.dl_bytes.get() + len(block))
                    self.percent.set(
                        int(100 * self.dl_bytes.get() / self.list_size))
                    f.write(block)
            except IOError:
                print("Error while writing file")
            try:
                r.close()
            except Exception:
                pass
            print('Done\n')
        return

    def go_to_next_page(self):
        """Search next page and pack prev button."""
        self.page = self.page + 1
        self.search_comics(None)
        self.prev_page.pack(side='left', padx=(50, 0))

    def go_to_prev_page(self):
        """Search previous page."""
        if self.page > 1:
            self.page = self.page - 1
            self.prev_page.pack_forget()
        else:
            self.page = 1
        self.search_comics(None)


# Main Loop
if __name__ == "__main__":
    app = Getcomics()  # constructor, calls method __init__
    app.mainloop()
