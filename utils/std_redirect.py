"""Module to redirect standard output."""

import customtkinter as ctk


class StdRedirector:
    """Redirect standard output Std into a frame in the GUI."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(ctk.END, message)
        self.text_widget.see(ctk.END)  # Fait défiler automatiquement vers la fin du texte

    def flush(self):
        pass  # Ne fait rien, car la sortie standard n'a pas de tampon à vider
