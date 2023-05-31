#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Get all new comics in getcomics weeklies."""

from pathlib import Path
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from typing import TypeAlias

import bs4

from utils import htmlsoup, getcomics
# Constants
from utils.const import DC_URL
# from utils.const import note, howto, howtodl, consistof
# from utils.const import lower, indieweek, bloat


Soup: TypeAlias = bs4.BeautifulSoup | bs4.Tag


def print_last_week(url: str):
    """Print time since last weekly pack.

    Args:
        url (str): getcomics tag url (/tag/*-week)
        editor (str): _description_
    """
    soup = htmlsoup.url2soup(url)
    last_post = soup.find_all('article', class_='type-post')[0]
    title = last_post.h1.a.text
    time = last_post.find('time')
    print(f'{title} :\t{time.text}')


def print_one_editor(soup: Soup, f, editor: str):
    """Write all comics in an editor weekly pack in file f.

    For Marvel, DC, or Image weeklies
    """
    strongs = soup.find_all('strong')

    f.write(editor + '\n')
    f.write("=====================\n")

    for s in strongs:  # strongs is a list of 'strong' divs
        name = s.contents[0].text.replace(' : ', '')
        a = s.find('a')
        try:
            # if a.has_attr('href'):
            if 'href' in a.attrs:
                f.write(f'[url={a.get("href")}]{name}[/url]\n')
        except Exception:
            f.write(name + '\n')
    f.write("=====================\n")
    f.write("" + '\n')


def print_multiple_editors(soup: Soup, f):
    """Write all comics in an Indies weekly pack in file f.

    For Indie week+.
    """
    publishers = soup.find_next_siblings("p")  # <p> tag is for publisher
    for p in publishers:
        if p.find('span') and "Notes :" not in p.text:
            f.write(f"\n{p.text.replace(':', '')}\n=====================\n")  # write publisher
            ul = p.find_next_sibling("ul")  # comics are in the <ul>, at same level as publisher <p>
            strongs = ul.select("ul > li > strong")
            for s in strongs:
                name = s.contents[0].text.replace(' : ', '')
                if s.a and s.a.has_attr('href'):
                    f.write(f'[url={s.a.get("href")}]{name}[/url]\n')
                else:
                    f.write(f'{name}\n')
    f.write('\n')


def generate_weekly():
    """Write all new comics in a file."""
    try:
        Path('liste-comics-semaine.txt').unlink(missing_ok=True)
    except OSError:
        print("ignoring file suppression OSError")

    _, weekly_url = getcomics.find_last_weekly(DC_URL)
    soup: bs4.BeautifulSoup = htmlsoup.url2soup(weekly_url)
    # titles = soup.select("section.post-contents > h3")
    titles = soup.select_one("section.post-contents").select("h3")

    with open("liste-comics-semaine.txt", "w") as f:
        for t in titles:
            if t.text in ("DC COMICS", "MARVEL COMICS", "IMAGE COMICS"):
                print_one_editor(t.next_sibling, f, t.text)
            elif t.text == "INDIE COMICS":
                print_multiple_editors(t, f)


# Select all the text in textbox
def select_all(event):
    widget = event.widget
    widget.tag_add(tk.SEL, "1.0", tk.END)
    widget.mark_set(tk.INSERT, "1.0")
    widget.see(tk.INSERT)
    return 'break'


if __name__ == "__main__":
    print("Le dernier 'weekly packs' de Getcomics est :")
    print("----------------")
    print_last_week(DC_URL)
    print("----------------")

    Join = input('Voulez-vous continuer ? (y/n) ?\n')
    if Join.lower() in ('yes', 'y'):
        print("Processing")
        generate_weekly()
        print("Done")
        # cmd = 'zenity --text-info --title="Sorties de la semaine"  ' \
        #       '--width=800 --height=600 --filename=liste-comics-semaine.txt'
        # subprocess.call(cmd, shell=True)

        txt = Path("liste-comics-semaine.txt").read_text()

        root = tk.Tk()
        root.title("Sorties Getcomics")

        text_widget = scrolledtext.ScrolledText(root, width=150)
        text_widget.insert(tk.END, txt)
        text_widget.pack(expand=True, fill='both')

        # Add the binding
        text_widget.bind("<Control-Key-a>", select_all)
        text_widget.bind("<Control-Key-A>", select_all)  # just in case caps lock is on  # noqa: E501

        tk.mainloop()

    else:
        print("Exit")
