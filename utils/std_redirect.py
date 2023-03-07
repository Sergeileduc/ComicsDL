#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module to redirect standard output."""

import tkinter as tk


class StdRedirector:
    """Redirect standard output Std into a frame in the GUI."""

    exit_thread = False
    exit_success = False

    def __init__(self, widget: tk.Text):
        """Init with widget."""
        self.widget = widget

    def write(self, string: str):
        """Write string in widget."""
        if not self.exit_thread:
            self.widget.insert(tk.END, string)
            self.widget.see(tk.END)

    def flush(self):
        """Flush."""
        pass
