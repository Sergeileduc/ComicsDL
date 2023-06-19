#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""GUI to download selected comics in getcomics.info weekly packs."""

import os
import sqlite3
import sys
import threading
import tkinter as tk
import tkinter.messagebox as msg

from utils.getcomics import get_weekly_comics
from utils.std_redirect import StdRedirector


class MyComicsList(tk.Tk):
    """GUI, made with tk.Tk."""

    def __init__(self, comic=None):
        """Init."""
        super().__init__()

        # List MyComicsList[] initialisation
        self.comics_buttons = comic or []
        w: int = 300  # width for the Tk
        h: int = 600  # height for the Tk
        # Get screen width and height
        ws: int = self.winfo_screenwidth()  # width of the screen
        hs: int = self.winfo_screenheight()  # height of the screen

        # Calculate x and y coordinates for the Tk root window
        x: float = (ws / 2) - (w / 2)
        y: float = (hs / 2) - (h / 2)
        longtext: str = ("Ajoutez ou supprimez les séries à chercher dans "
                         "les derniers posts \n\"Weekly\" de Getcomics.info")

        ascii_title: str = """
██████╗ ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗██╗ ██████╗███████╗
██╔════╝ ██╔════╝╚══██╔══╝██╔════╝██╔═══██╗████╗ ████║██║██╔════╝██╔════╝
██║  ███╗█████╗     ██║   ██║     ██║   ██║██╔████╔██║██║██║     ███████╗
██║   ██║██╔══╝     ██║   ██║     ██║   ██║██║╚██╔╝██║██║██║     ╚════██║
╚██████╔╝███████╗   ██║   ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║╚██████╗███████║
 ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝╚══════╝"""

        # Basic window stuff.
        self.title("Télécharger All V2023-03")
        self.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

        # Message and Logo
        self.ascii_title = tk.Label(self, text=ascii_title, anchor=tk.W, justify=tk.LEFT,
                                    font=("Courier", 4))
        self.welcome_message = tk.Label(self, text=longtext, anchor=tk.W, justify=tk.CENTER,
                                        wraplength=250, font=("Helvetica", 12))

        # Comics scrollable list / input textbox / download button
        self.comic_canvas = tk.Canvas(self)
        self.comic_frame = tk.Frame(self.comic_canvas)
        self.text_frame = tk.Frame(self)  # add comic frame (will contain a text widget)
        self.output_text = tk.Text(self, bg="black", fg="white")  # std text widget
        self.button = tk.Button(self, text="Télécharger les comics",  # 'Télécharger' button
                                command=self.run)
        self.scrollbar_comics = tk.Scrollbar(self.comic_canvas,
                                             orient="vertical",
                                             command=self.comic_canvas.yview)
        self.comic_canvas.configure(yscrollcommand=self.scrollbar_comics.set)

        self.comic_create = tk.Text(self.text_frame,  # Text input to add a comic
                                    height=3, bg="white", fg="black")

        # PACKING
        self.ascii_title.pack()  # pack to root
        self.welcome_message.pack()  # pack to root
        self.comic_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollbar_comics.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_frame = self.comic_canvas.create_window((0, 0),
                                                            window=self.comic_frame,
                                                            anchor="n")

        # self.text_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_frame.pack()
        self.button.pack()
        self.comic_create.pack()
        self.output_text.pack(side=tk.BOTTOM, fill=tk.X)
        # self.button.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_idletasks()

        # self.comic_create.pack(side=tk.BOTTOM, fill=tk.X)

        self.comic_create.focus_set()

        self.colour_schemes = [{"bg": "lightgrey", "fg": "black"}, {"bg": "grey", "fg": "white"}]

        current_comic = self.load_comics_database()
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
        current_comic = self.load_comics_database()
        # comics_list = [row[0].lower().replace(' ', '-') for row in current_comic]
        comics_list = [row[0].lower() for row in current_comic]
        thread1 = threading.Thread(target=get_weekly_comics, args=[comics_list])
        thread1.start()

    def add_comic(self, event=None, comic_text: str = None, from_db=False):
        """Add comic - create new button and add comic in the database."""
        if not comic_text:
            comic_text = self.comic_create.get(1.0, tk.END).strip()

        if len(comic_text) > 0:
            new_comic: tk.Label = tk.Label(self.comic_frame, text=comic_text, pady=10)

            self.set_comic_colour(len(self.comics_buttons), new_comic)

            new_comic.bind("<Button-1>", self.remove_comic)
            new_comic.pack(side=tk.TOP, fill=tk.X)

            self.comics_buttons.append(new_comic)

            if not from_db:
                self.save_comic(comic_text)

        self.comic_create.delete(1.0, tk.END)

    def remove_comic(self, event: tk.Event):
        """Remove comic - delete button and remove from database."""
        comic_button: tk.Label = event.widget
        if msg.askyesno(
                "Confirmation de suppressions",
                f"Supprimer {comic_button.cget('text')} de la liste ?"):
            self.comics_buttons.remove(comic_button)

            delete_comic_query = "DELETE FROM comics WHERE comic=?"
            delete_comic_data = (comic_button.cget("text"),)
            self.run_query(delete_comic_query, delete_comic_data)

            comic_button.destroy()
            self.recolour_comic()

    def recolour_comic(self):
        """Recolor comics recursively."""
        for index, comic in enumerate(self.comics_buttons):
            self.set_comic_colour(index, comic)

    def set_comic_colour(self, position: int, comic):
        """Recolour comics (odd or even in the list)."""
        _, comic_style_choice = divmod(position, 2)

        my_scheme_choice = self.colour_schemes[comic_style_choice]

        comic.configure(bg=my_scheme_choice["bg"])
        comic.configure(fg=my_scheme_choice["fg"])

    def _on_frame_configure(self, event=None):
        self.comic_canvas.configure(scrollregion=self.comic_canvas.bbox("all"))

    def _comic_width(self, event: tk.Event):
        canvas_width = event.width
        self.comic_canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def _mouse_scroll(self, event: tk.Event):
        if event.delta:
            self.comic_canvas.yview_scroll(-1 * (event.delta / 120), "units")
        else:
            move = 1 if event.num == 5 else -1
            self.comic_canvas.yview_scroll(move, "units")

    @staticmethod
    def save_comic(comic):
        """Add new comic in database."""
        insert_comic_query = "INSERT INTO comics VALUES (?)"
        insert_comic_data = (comic,)
        MyComicsList.run_query(insert_comic_query, insert_comic_data)

    @staticmethod
    def load_comics_database() -> list:
        """Read database.

        Returns:
            list: list of comics in the database (1-tuples)
        """
        return MyComicsList.run_query("SELECT comic FROM comics", receive=True)

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
        create_table1 = "CREATE TABLE IF NOT EXISTS comics (comic TEXT)"
        MyComicsList.run_query(create_table1)

        default_comic_data = ("--- Ajoutez vos séries de comics ---",)
        default_dc_query = "INSERT INTO comics VALUES (?)"
        MyComicsList.run_query(default_dc_query, default_comic_data)

# thread1 = threading.Thread(target=call_gen)


if __name__ == "__main__":
    if not os.path.isfile(".comics.db"):
        MyComicsList.first_time_db()
    comicsList = MyComicsList()
    comicsList.mainloop()
