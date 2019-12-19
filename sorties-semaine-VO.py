#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Get all new comics in getcomics weeklies."""

import copy
import os
# import subprocess
import tkinter as tk

from utils import htmlsoup, getcomics
# Constants
from utils.const import DC_URL, MARVEL_URL, IMAGE_URL, INDIE_URL
from utils.const import note, howto, howtodl, consistof
from utils.const import lower, indieweek, bloat


def print_last_weeklies():
    """Find last weeklies and print."""
    print_last_week(DC_URL, "DC")
    print_last_week(MARVEL_URL, "Marvel")
    print_last_week(IMAGE_URL, "Image")
    print_last_week(INDIE_URL, "Indé")


def print_last_week(url, editor):
    """Print time since last weekly pack."""
    soup = htmlsoup.url2soup(url)
    last_post = soup.find_all('article', class_='type-post')[0]
    title = last_post.h1.a.text
    time = last_post.find('time')
    print(f'{editor}\t : {title} :\t{time.text}')


def print_week(url, f, editor):
    """Write all comics of 'editor' weekly pack in file f."""
    global flag
    flag = False
    post_title, weekly_url = getcomics.find_last_weekly(url)

    # Missing post already been done
    if "Missing" in post_title and flag:
        pass
    # Missing post not done yet
    elif "Missing" in post_title and not flag:
        f.write(post_title + '\n')
        f.write("=====================\n")
        print_multiple_editors(weekly_url, f)
        flag = True
    elif editor == "Indé week":
        print_multiple_editors(weekly_url, f)
    else:
        print_one_editor(weekly_url, f, editor)


def print_one_editor(url, f, editor):
    """Write all comics in an editor weekly pack in file f.

    For Marvel, DC, or Image weeklies
    """
    soup = htmlsoup.url2soup(url)
    var = soup.select_one('section.post-contents > ul').find_all('strong')

    f.write(editor + '\n')
    f.write("=====================\n")
    for s in var:  # var is a list of 'strong' divs
        s_copy = copy.copy(s)
        for _ in s_copy:
            s_copy.span.decompose()
        name = s_copy.text.replace(' : ', '').replace('| ', '')
        a = s.find('a')
        try:
            # if a.has_attr('href'):
            if 'href' in a.attrs:
                f.write(f'[url={a.get("href")}]{name}[/url]\n')
        except Exception:
            f.write(name + '\n')
    f.write("=====================\n")
    f.write("" + '\n')


def print_multiple_editors(url, f):
    """Write all comics in an Indies weekly pack in file f.

    For Indie week+.
    """
    soup = htmlsoup.url2soup(url).select_one('section.post-contents')

    # List of comics publishers
    publishers = soup.find_all('span', style="color: #3366ff;")
    indies = [p.text for p in publishers]

    # List of comics
    var = soup.find_all('strong')
    for s in var:
        # Highlight publishers
        if s.text in indies:
            f.write(f'\n{s.text}\n=====================\n')
        # blots
        elif (note in s.text
              or howto in s.text
              or consistof in s.text
              or howtodl in s.text
              or lower in s.text
              or indieweek in s.text):
            pass
        # more bloats
        elif s.text in bloat:
            pass
        # Comics
        else:
            # make a copy of strong s to remove span
            s_copy = copy.copy(s)
            for _ in s_copy:
                try:
                    s_copy.span.decompose()
                except AttributeError:
                    pass
            name = s_copy.text.replace(' : ', '').replace('| ', '')
            if s.a and s.a.has_attr('href'):
                f.write(f'[url={s.a.get("href")}]{name}[/url]\n')
            else:
                f.write(f'{name}\n')
    f.write('\n')


def generate_weekly():
    """Write all new comics in a file."""
    global flag
    flag = False
    try:
        os.remove('liste-comics-semaine.txt')
    except OSError:
        pass

    with open("liste-comics-semaine.txt", "w") as f:
        print_week(DC_URL, f, "DC week")
        print_week(MARVEL_URL, f, "Marvel week")
        f.write("Indé week" + '\n')
        f.write("=====================" + '\n')
        print_week(IMAGE_URL, f, "Image week")
        print_week(INDIE_URL, f, "Indé week")


# MAIN
print("Les derniers 'weekly packs' de Getcomics sont :")
print("----------------")
print_last_weeklies()
print("----------------")

Join = input('Voulez-vous continuer ? (y/n) ?\n')
if Join.lower() == 'yes' or Join.lower() == 'y':
    print("Processing")
    generate_weekly()
    print("Done")
    # cmd = 'zenity --text-info --title="Sorties de la semaine"  ' \
    #       '--width=800 --height=600 --filename=liste-comics-semaine.txt'
    # subprocess.call(cmd, shell=True)

    with open("liste-comics-semaine.txt", "r") as f:
        txt = f.read()

    root = tk.Tk()
    T = tk.Text(root, width=150)
    T.pack(fill="both", expand=1)
    T.insert(tk.END, txt)
    tk.mainloop()

else:
    print("Exit")
