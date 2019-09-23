#!/usr/bin/python3
# -*-coding:utf-8 -*-

import tkinter as tk


# Redirect standard output Std into a frame in the GUI
class StdRedirector(object):

    exit_thread = False
    exit_success = False

    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        if not self.exit_thread:
            self.widget.insert(tk.END, string)
            self.widget.see(tk.END)

    def flush(self):
        pass
