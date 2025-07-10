"the page panel: shows what pages are in the top level category chosen by the what panel."

import tkinter as tk
from tkinter import E, N, S, W, ttk

import gendata as dat
from enums import HEIGHT, WIDTH, State, Widgets


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

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))

        self.add_button = ttk.Button(self.button_frame, text="New Form", command=self.do_new_form)
        self.add_button = ttk.Button(self.button_frame, text="New List", command=self.do_new_list)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=2)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._cur_page = None

    def set_page(self, lst: list):
        "sets the contents of the page panel"
        self._cur_page = lst
        self.page_choices.set([n for n, _ in self._cur_page])

    def do_page(self, e):  # pylint: disable=unused-argument
        "Dispatches based on state"
        match self._parent.state:
            case State.ROLL:
                self.do_page_roll()
            case State.EDIT:
                self.do_page_edit()

    def do_page_edit(self):
        "Handle 'page' coloumn edit mode"

    def do_page_roll(self):
        "handles the 'page' column to choose which table, page, or formula to generate from; triggers re-roll"
        if self._cur_page is None:
            return

        sel = self._page.curselection()
        if len(sel) == 1:
            _, form = self._cur_page[sel[0]]
            self._parent.set_formula(self._cur_page[sel[0]])
            self._parent.result_ungrid_set()

            match form:
                case dat.Formula():
                    self._parent.result_grid_set(Widgets.FORM)
                case list():
                    self._parent.result_grid_set(Widgets.ROLL)

            self._parent.reroll()

    def set_state(self):
        "set state handler called when _parent changes state"

    def do_new_form(self):
        "Do new Form button"

    def do_new_list(self):
        "Do new list button"
