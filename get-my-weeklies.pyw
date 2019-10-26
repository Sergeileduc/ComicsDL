#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""GUI to download selected comics in getcomics.info weekly packs."""

import sys
import os
import tkinter as tk
import tkinter.messagebox as msg
import sqlite3
import threading

from utils.getcomics import get_weekly_comics

exit_thread = False
exit_success = False


class StdRedirector(object):
    """Redirect std output in a widget."""

    def __init__(self, widget):
        """Init Stdredirector (debug) widget."""
        self.widget = widget

    def write(self, string):
        """Insert stdout in widget."""
        if not exit_thread:
            self.widget.insert(tk.END, string)
            self.widget.see(tk.END)

    def flush(self):
        """Flush."""
        pass


class MyComicsList(tk.Tk):
    """GUI, made with tk.Tk."""

    def __init__(self, comic=None):
        """Init."""
        super().__init__()

        # List MyComicsList[] initialisation
        if not comic:
            self.comic = []
        else:
            self.comic = comic

        w = 300  # width for the Tk
        h = 600  # height for the Tk
        # Get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen

        # Calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        longtext = ("Ajoutez ou supprimez les séries à chercher dans "
                    "les derniers posts \n\"Weekly\" de Getcomics.info")
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

        self.comic_canvas = tk.Canvas(self)
        self.message = tk.Label(
            self, text=longtext, anchor=tk.W, justify=tk.CENTER,
            wraplength=250, font=("Helvetica", 12))
        self.ascii_title = tk.Label(self, text=ascii_title,
                                    anchor=tk.W, justify=tk.LEFT,
                                    font=("Courier", 4))
        self.comic_frame = tk.Frame(self.comic_canvas)
        self.text_frame = tk.Frame(self)
        self.output_text = tk.Text(self, bg="black", fg="white")
        self.button = tk.Button(self,
                                text="Télécharger les comics",
                                command=self.run)
        self.scrollbar = tk.Scrollbar(self.comic_canvas,
                                      orient="vertical",
                                      command=self.comic_canvas.yview)
        self.comic_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.title("Télécharger All V2019-07")
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
        self.comic_create = tk.Text(self.text_frame, height=3,
                                    bg="white", fg="black")

        self.ascii_title.pack()
        self.message.pack()
        self.comic_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_frame = self.comic_canvas.create_window(
            (0, 0), window=self.comic_frame, anchor="n")

        # self.text_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_frame.pack()
        self.button.pack()
        self.comic_create.pack()
        self.output_text.pack(side=tk.BOTTOM, fill=tk.X)
        # self.button.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_idletasks()

        # self.comic_create.pack(side=tk.BOTTOM, fill=tk.X)

        self.comic_create.focus_set()

        self.colour_schemes = [
            {"bg": "lightgrey", "fg": "black"}, {"bg": "grey", "fg": "white"}]

        current_comic = self.load_comic()
        for comic in current_comic:
            comic_text = comic[0]
            self.add_comic(None, comic_text, True)

        self.bind("<Return>", self.add_comic)
        self.bind("<Configure>", self._on_frame_configure)
        self.bind_all("<MouseWheel>", self._mouse_scroll)
        self.bind_all("<Button-4>", self._mouse_scroll)
        self.bind_all("<Button-5>", self._mouse_scroll)
        self.comic_canvas.bind("<Configure>", self._comic_width)

    def run(self):
        """Run download."""
        sys.stdout = StdRedirector(self.output_text)
        current_comic = self.load_comic()
        comics_list = [row[0].lower().replace(' ', '-') for row in current_comic]  # noqa: E501
        thread1 = threading.Thread(target=get_weekly_comics, args=[comics_list])  # noqa: E501
        thread1.start()

    def add_comic(self, event=None, comic_text=None, from_db=False):
        """Add comic - create new button and add comic in the database."""
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
        """Remove comic - delete button and remove from database."""
        comic = event.widget
        if msg.askyesno(
                "Confirmation de suppressions",
                f"Supprimer {comic.cget('text')} de la liste ?"):
            self.comic.remove(event.widget)

            delete_comic_query = "DELETE FROM comics_dc WHERE comic=?"
            delete_comic_data = (comic.cget("text"),)
            self.run_query(delete_comic_query, delete_comic_data)

            event.widget.destroy()

            self.recolour_comic()

    def recolour_comic(self):
        """Recolor comics recursively."""
        for index, comic in enumerate(self.comic):
            self.set_comic_colour(index, comic)

    def set_comic_colour(self, position, comic):
        """Recolour comics (odd or even in the list)."""
        _, comic_style_choice = divmod(position, 2)

        my_scheme_choice = self.colour_schemes[comic_style_choice]

        comic.configure(bg=my_scheme_choice["bg"])
        comic.configure(fg=my_scheme_choice["fg"])

    def _on_frame_configure(self, event=None):
        self.comic_canvas.configure(scrollregion=self.comic_canvas.bbox("all"))

    def _comic_width(self, event):
        canvas_width = event.width
        self.comic_canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def _mouse_scroll(self, event):
        if event.delta:
            self.comic_canvas.yview_scroll(-1 * (event.delta / 120), "units")
        else:
            move = 1 if event.num == 5 else -1
            self.comic_canvas.yview_scroll(move, "units")

    def save_comic(self, comic):
        """Add new comic in database."""
        insert_comic_query = "INSERT INTO comics_dc VALUES (?)"
        insert_comic_data = (comic,)
        self.run_query(insert_comic_query, insert_comic_data)

    def load_comic(self):
        """Read database."""
        load_comic_query = "SELECT comic FROM comics_dc"
        my_comic = self.run_query(load_comic_query, receive=True)
        return my_comic

    @staticmethod
    def run_query(sql, data=None, receive=False):
        """Run sql query."""
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
    def first_time_db():
        """Create database tables."""
        create_table1 = "CREATE TABLE IF NOT EXISTS comics_dc (comic TEXT)"
        MyComicsList.run_query(create_table1)
        create_table2 = "CREATE TABLE IF NOT EXISTS comics_marvel (comic TEXT)"
        MyComicsList.run_query(create_table2)
        create_table3 = "CREATE TABLE IF NOT EXISTS comics_indies (comic TEXT)"
        MyComicsList.run_query(create_table3)
        create_table4 = "CREATE TABLE IF NOT EXISTS comics_image (comic TEXT)"
        MyComicsList.run_query(create_table4)

        default_comic_data = ("--- Ajoutez vos séries de comics ---",)
        default_dc_query = "INSERT INTO comics_dc VALUES (?)"
        MyComicsList.run_query(default_dc_query, default_comic_data)
        default_marvel_query = "INSERT INTO comics_marvel VALUES (?)"
        MyComicsList.run_query(default_marvel_query, default_comic_data)
        default_indie_query = "INSERT INTO comics_indies VALUES (?)"
        MyComicsList.run_query(default_indie_query, default_comic_data)
        default_image_query = "INSERT INTO comics_image VALUES (?)"
        MyComicsList.run_query(default_image_query, default_comic_data)

# thread1 = threading.Thread(target=call_gen)


if __name__ == "__main__":
    if not os.path.isfile(".comics.db"):
        MyComicsList.first_time_db()
    comicsList = MyComicsList()
    comicsList.mainloop()
