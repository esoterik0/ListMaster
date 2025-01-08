"the page panel: shows what pages are in the top level category chosen by the what panel."

import tkinter as tk
from tkinter import E, N, S, W, ttk

import gendata as dat
from enums import HEIGHT, WIDTH, Widgets


class PagePanel(ttk.Frame):  # pylint: disable=too-many-ancestors
    "generates the page frame, for choosing, inspecting, or editing which 'page', formula or table"
    def __init__(self, parent, **kwargs):
        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=1, row=0, sticky=(N, S, E, W))
        self._parent = parent

        self.page_choices = tk.StringVar()

        self._page = tk.Listbox(self, listvariable=self.page_choices, width=int(3*WIDTH/5), height=HEIGHT)
        self._page.grid(column=0, row=0, sticky=(N, S, E, W))
        self._page.bind("<<ListboxSelect>>", self.do_page)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._cur_page = None

    def set_page(self, lst: list):
        "sets the contents of the page panel"
        self._cur_page = lst
        self.page_choices.set([n for n, _ in self._cur_page])

    def do_page(self, e):  # pylint: disable=unused-argument
        "handles the 'page' column to choose which table, page, or formula to generate from; triggers re-roll"
        if self._cur_page is None:
            return

        sel = self._page.curselection()
        if len(sel) == 1:
            _, form = self._cur_page[sel[0]]
            self._parent.set_formula(self._cur_page[sel[0]])
            self._parent.grid_set(Widgets.ROLL)

            if isinstance(form, dat.Formula):
                self._parent.grid_set(Widgets.FORM)
            else:
                self._parent.ungrid_set(Widgets.FORM)

            self._parent.reroll()
