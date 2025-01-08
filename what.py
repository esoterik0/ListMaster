"the what panel: chooses what top level category to use."

import tkinter as tk
from tkinter import E, N, S, W, ttk

from enums import HEIGHT, WIDTH, Widgets


class WhatPanel(ttk.Frame):  # pylint: disable=too-many-ancestors
    "generates the What panel, for choosing what top level category to use"
    def __init__(self, parent, **kwargs):
        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self._parent = parent

        self.what_list = []
        self.choices = []
        self.what_choice_var = tk.StringVar()

        self.what = tk.Listbox(self, listvariable=self.what_choice_var, width=int(WIDTH/5), height=HEIGHT)
        self.what.grid(column=0, row=0, sticky=(N, S, E, W))
        self.what.bind("<<ListboxSelect>>", self.do_what)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def set_what(self, lst, choice):
        "sets the values for the what panel, the list needs to have data in it, choice should have the labels."
        self.what_list = lst
        self.choices = choice
        self.what_choice_var.set(choice)

    def get_what(self) -> tuple[list, list]:
        "gets the top level what lists"
        return self.what_list, self.choices

    def do_what(self, e):  # pylint: disable=unused-argument
        "handles the 'what' column, which is the top level category, and fills out the page choices"
        sel = self.what.curselection()

        if len(sel) == 1:
            self._parent.set_page(self.what_list[sel[0]])
            self._parent.set_result([])
            self._parent.ungrid_set(Widgets.ROLL, Widgets.FORM)
