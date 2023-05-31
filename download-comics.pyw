#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""GUI to download comics on getcomics.info."""
import sys
import threading
import customtkinter as ctk
import tkinter as tk
from typing import NamedTuple

import requests
from requests.exceptions import HTTPError
from tqdm import tqdm

from utils import getcomics
from utils.getcomics import getcomics_directlink, DLurlError, getresults, PostInfos
from utils.std_redirect import StdRedirector
from utils.tools import bytes_2_human_readable, convert2bytes, remove_tag
from utils.urltools import getfinalurl


class DownloadInQueue(NamedTuple):
    title: str
    url: str
    size: str = None
    button: ctk.CTkButton = None


class TopBarFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.user_search = ctk.StringVar()
        self.choices = ['Recherche par TAG', 'Recherche simple']
        self.mode = ctk.StringVar(value='Recherche simple')
        self.choice_menu = ctk.CTkOptionMenu(self,
                                             values=['Recherche par TAG', 'Recherche simple'],
                                             variable=self.mode)
        self.search_entry = ctk.CTkEntry(self, textvariable=self.user_search, justify='center',
                                         placeholder_text="Rechercher un comicbook")
        self.search_entry.pack(side='left', expand=True, fill="x")
        self.choice_menu.pack(side='right')
        self.search_entry.focus_set()
        self.search_entry.bind("<Return>", self.master.search_comics)


class NavigationBar(ctk.CTkFrame):
    def __init__(self, master, top, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.top = top
        self.prev_page = ctk.CTkButton(self,
                                       text="page précédente",
                                       command=self.go_to_prev_page)
        self.next_page = ctk.CTkButton(self,
                                       text="page suivante",
                                       command=self.go_to_next_page)
        self.next_page.pack(side='right', padx=(0, 50))

    def go_to_next_page(self) -> None:
        """Search next page and pack prev button."""
        self.top.page += 1
        self.top.search_comics(None)
        self.prev_page.pack(side='left', padx=(50, 0))

    def go_to_prev_page(self) -> None:
        """Search previous page."""
        if self.top.page > 1:
            self.top.page -= 1
            self.prev_page.pack_forget()
        else:
            self.top.page = 1
        self.top.search_comics(None)


class LeftFrame(ctk.CTkFrame):
    def __init__(self, master, top, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.top = top
        # self.instructions = ctk.CTkLabel(self, text='Cliquez pour ajouter un élément '
        #                                             'à votre liste de téléchargement')
        self.result_frame = ctk.CTkScrollableFrame(self,
                                                   label_text='Cliquez pour ajouter un élément '
                                                              'à votre liste de téléchargement',
                                                   label_font=ctk.CTkFont(size=12, weight="bold"))
        self.navigation_bar = NavigationBar(self, top, fg_color="transparent")
        # self.instructions.pack(fill='x')
        self.result_frame.pack(side='top', expand=True, fill='both')
        self.navigation_bar.pack(side='bottom', anchor='sw', fill='x')


class RightFrame(ctk.CTkFrame):
    def __init__(self, master, top, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.top = top
        # self.liste_label = ctk.CTkLabel(self, text="Liste de téléchargement")
        self.dl_frame = ctk.CTkScrollableFrame(self, label_text="Liste de téléchargement",
                                               label_font=ctk.CTkFont(size=20, weight="bold"))
        self.dl_all_button = ctk.CTkButton(self, text="Télécharger la liste",
                                           command=lambda: self.top.dl_com(self.master.download_list))  # noqa: E501
        # self.liste_label.pack(fill='x')
        self.dl_frame.pack(side='top', expand=True, fill='both')
        self.dl_all_button.pack(side='bottom', fill='x')


class MainFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.top = master
        self.left_frame = LeftFrame(self, top=master, fg_color="transparent")
        self.right_frame = RightFrame(self, top=master, fg_color="transparent")
        self.result_frame = self.left_frame.result_frame
        self.left_frame.pack(side='left', anchor='nw', fill='both', expand=True, padx=(0, 10))
        self.right_frame.pack(side='right', anchor='ne', fill='both', expand=True, padx=(10, 0))

        self.list_size: int = 0  # size of the download list in bytes
        self.search_results_list: list[PostInfos] = []
        self.search_button_list: list[ctk.CTkButton] = []
        self.download_list: list[DownloadInQueue] = []
        self.download_button_list: list[ctk.CTkButton] = []

    def add_to_dl(self, button: ctk.CTkButton) -> None:
        """Click to add to DL list."""
        index = self.search_button_list.index(button)
        comic = button.cget('text')
        if comic not in (item.title for item in self.download_list):
            if self.search_results_list[index].size:
                size_bytes = convert2bytes(self.search_results_list[index].size)
                self.list_size += size_bytes
            new_dl_button = ctk.CTkButton(self.right_frame.dl_frame,
                                          text=button.cget('text').title(), corner_radius=0)
            new_dl_button.configure(command=lambda button=new_dl_button: self.remove_dl(button))
            new_dl_button.pack(fill='both', expand=1, pady=0)
            self.download_list.append(
                DownloadInQueue(title=self.search_results_list[index].title,
                                url=self.search_results_list[index].url,
                                size=self.search_results_list[index].size,
                                button=new_dl_button))
            self.download_button_list.append(new_dl_button)
            total_size = bytes_2_human_readable(self.list_size)
            print(f"Taille de la file d'attente (donnée indicative) : "
                  f"{total_size}")
        else:
            print("Already in your DL list")

    def remove_dl(self, button: ctk.CTkButton) -> None:
        """Click to remove an item function."""
        for to_download in self.download_list:
            if button == to_download.button:
                if to_download.size:
                    bytes_ = convert2bytes(to_download.size)
                    self.list_size -= bytes_
                self.download_list.remove(to_download)
        self.download_button_list.remove(button)
        button.destroy()
        total_size = bytes_2_human_readable(self.list_size)
        print(f"Taille de la file d'attente (donnée indicative) : {total_size}")


# Main program interface and code
class Getcomics(ctk.CTk):
    """GUI made with tk.TK."""

    def __init__(self):  # pylint: disable=too-many-locals
        """Init Tkinter program with GUI."""
        super().__init__()
        self.title("Télécharger sur Getcomics 2021-06")
        size_x = 900  # width
        size_y = 600  # height

        # Gets both half the screen width/height and window width/height
        pos_x = int(self.winfo_screenwidth() / 2 - size_x / 2)
        pos_y = int(self.winfo_screenheight() / 2 - size_y / 2)

        self.page: int = 1
        self.current_percent = ctk.DoubleVar(value=0.0)
        self.percent = ctk.DoubleVar(value=0.0)
        self.dl_bytes = ctk.IntVar(value=0)
        self.wm_geometry(f"{size_x}x{size_y}+{pos_x}+{pos_y}")

        self.top_bar = TopBarFrame(self, fg_color="transparent")
        self.main_frame = MainFrame(self, fg_color="transparent")

        self.bottom_bar = ctk.CTkFrame(self)
        self.output_text = ctk.CTkTextbox(self.bottom_bar, height=100)
        self.progress = ctk.CTkProgressBar(self.bottom_bar, orientation="horizontal",
                                           variable=self.current_percent,
                                           mode="determinate")
        self.progress2 = ctk.CTkProgressBar(self.bottom_bar, orientation="horizontal",
                                            variable=self.percent,
                                            mode="determinate")

        self.top_bar.pack(fill='x', anchor='n', padx=20, pady=20)
        self.main_frame.pack(fill='both', expand=1, anchor='nw',
                             padx=20, pady=(0, 5))

        self.bottom_bar.pack(fill='x')
        self.progress.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        self.progress2.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        self.output_text.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        sys.stdout = StdRedirector(self.output_text)

        # self.search_comics(None)

    @staticmethod
    def destroy_list(widget_list: list[tk.Widget]) -> None:
        """Destroy a list of widgets (like buttons)."""
        for w in widget_list:
            w.destroy()
            print("Destroyed", w)
        widget_list.clear()

    # Search comics function
    def search_comics(self, event) -> None:
        """Search comic on getcomics.info."""
        print("Search")
        self.main_frame.search_results_list.clear()
        self.destroy_list(self.main_frame.search_button_list)
        search_mode = self.top_bar.choices.index(self.top_bar.mode.get())
        search_url = getcomics.searchurl(self.top_bar.user_search.get(), search_mode, self.page)
        self.main_frame.search_results_list = getresults(search_url)

        for res in self.main_frame.search_results_list:
            title = f'{res.title} ({res.size})'
            new_button = ctk.CTkButton(self.main_frame.result_frame,
                                       text=title, corner_radius=0)
            new_button.configure(
                command=lambda button=new_button: self.main_frame.add_to_dl(button))
            new_button.pack(fill='both', expand=1, pady=0)
            self.main_frame.search_button_list.append(new_button)

    def dl_com(self, dl_list: list[DownloadInQueue]) -> None:
        try:
            thread1 = threading.Thread(target=self.down_all_com, args=[dl_list])
            thread1.start()
        except Exception as exc:
            print(exc)

    def down_all_com(self, dl_list: list[DownloadInQueue]) -> None:
        """Download all comics in the list."""
        self.dl_bytes.set(0)
        for dl in dl_list:
            try:
                self.download_comic(dl.url)
            except Exception as e:
                print("down_all_com got an Error :")
                print(f"{type(e).__name__} : {e}")
        self.percent.set(0)
        print("Destruction des boutons de droite")
        self.destroy_list(self.main_frame.download_button_list)
        print("Terminé, vous pouvez quitter")

    def download_comic(self, url: str) -> None:
        """Find download url, download.

        Args:
            url (str): getcomics "post" url for a comicbook
        """
        final_url: str = getfinalurl(url)  # handle possible redirecteions
        print(f"download_comic function with : {final_url}")
        try:
            direct_url, name, size = getcomics_directlink(final_url)
        except DLurlError as e:
            print(f"download_comic got Error : {e}")
        except HTTPError as e:
            print(f"download_comic got Error : {e}")
            raise
        try:
            print(f"{direct_url = }")
            print(f"{name = }")
            print(f"{size = }")
            self._write_comics(direct_url, name, size)
        except Exception as e:
            print("error in download_comic")
            print(f"download_comic got Error : {e}")

    def _write_comics(self, url: str, name: str, size: int) -> None:
        self.progress["value"] = 0
        try:
            r: requests.Response = requests.get(url, stream=True)
            print(f"size = {bytes_2_human_readable(size)}")
        except Exception as e:
            print("Can't get download link")
            print(f"_write_comics error {e}")

        # Download from url & trim it a little bit
        with open(remove_tag(name), 'wb') as f:
            try:
                dl = 0
                if self.main_frame.list_size == 0:
                    self.main_frame.list_size = 1
                for block in tqdm(iterable=r.iter_content(51200), total=size / 51200):
                    dl += len(block)
                    self.current_percent.set(dl / size)
                    self.dl_bytes.set(self.dl_bytes.get() + len(block))
                    self.percent.set(self.dl_bytes.get() / self.main_frame.list_size)
                    f.write(block)
            except IOError:
                print("_write_comics : Error while writing file")
            try:
                r.close()
            except Exception as e:
                print(e)
            print('Done\n')


# Main Loop
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    app = Getcomics()  # constructor, calls method __init__
    app.mainloop()
