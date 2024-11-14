"listmaster: roll on random tables; create and edit random tables;"

import tkinter as tk
from enum import Enum
from tkinter import E, N, S, W, filedialog, ttk

import dill as pickle

import gendata as dat

WIDTH = 75
HEIGHT = 25
SINGLE = 5
DATA = "tables.dat"


class Widgets(Enum):
    "enums to define which widgets to grid and ungrid at various points"
    ROLL = 1
    FORM = 2


def int_nun(s: str) -> int | None:
    "returns the int represented by the string or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


class WhatPanel(ttk.Frame):
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


class PagePanel(ttk.Frame):
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


class ResultsPanel(ttk.Frame):
    "generates the page frame, for choosing, inspecting, or editing which 'page', formula or table"
    def __init__(self, parent, **kwargs):
        self._parent = parent
        self.num = SINGLE
        self.path = ""
        self.form = None
        self.form_name = ""

        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=2, row=0, sticky=(N, S, E, W))

        self.results = tk.StringVar()
        self.result_list = []

        self.result = tk.Listbox(self, listvariable=self.results, width=int(4*WIDTH/5), height=HEIGHT)
        self.result.grid(column=0, row=0, sticky=(N, S, E, W))

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))

        self.reroll = ttk.Button(self.button_frame, text="Re-Roll", command=self.do_reroll)
        self.reroll.grid(column=0, row=0)

        self.num_pages_label = ttk.Label(self.button_frame, text="No. Pages")
        self.num_pages_label.grid(column=0, row=1)

        self.num_pages_var = tk.StringVar()
        self.num_pages_var.set(f"{SINGLE}")

        self.num_pages = tk.Entry(self.button_frame, textvariable=self.num_pages_var)
        self.num_pages.grid(column=1, row=1)

        self.clip_copy = ttk.Button(self.button_frame, text="Copy to clip board", command=self._copy_clip)
        self.clip_copy.grid(column=1, row=0)

        self.gen_xls = ttk.Button(self.button_frame, text="Generate .xls file", command=self.do_xls)
        self.gen_xls.grid(column=2, row=1)

        self.get_path = ttk.Button(self.button_frame, text="Choose path", command=self.do_path)
        self.get_path.grid(column=2, row=0)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

    def set_formula(self, form):
        "sets the formula or table to roll on"
        self.form_name, self.form = form

    def do_reroll(self):
        "handles the re-roll button, generates and populates the results column"
        if self.form is not None:
            match(self.form):
                case list():
                    self._update_num()
                    self.result_list = [self.form_name] + [dat.gen_list(self.form) for _ in range(self.num)]
                case dat.Formula():
                    self.result_list = [
                        b + ": " + o
                        for b, o in zip(
                            self.form.labels,
                            dat.gen_form(self.form)
                        )
                    ]
        else:
            self.result_list = []
        self.set_result(self.result_list)

    def set_result(self, lst: list):
        "sets the results string, used for clearing the list"
        self.results.set(lst)

    def do_path(self):
        "gets the path"
        self.path = filedialog.askdirectory()
        if self.path:
            self.path += "/"

    def _update_num(self):
        "updates self.num"
        num = int_nun(self.num_pages_var.get())  # try to get the number
        self.num = num if num else SINGLE  # if we don't have a number num is None

    def do_xls(self):
        "Handles the Generate .xls button, currently makes double sided three hole punched 8 1/2 x 11 pages."
        self._update_num()
        dat.manufacture(self.form, self.path, self.form_name, self.num)

    def _copy_clip(self):
        "copy the results to the clipboard"
        self._parent.clipboard("\n".join(self.result_list))

    def ungrid_set(self, *widgets: Widgets):
        "removes widgets from the grid"
        for w in widgets:
            match w:
                case Widgets.ROLL:
                    self.reroll.grid_remove()
                    self.button_frame.grid_remove()
                case Widgets.FORM:
                    self.gen_xls.grid_remove()
                    self.get_path.grid_remove()
                    self.num_pages_label.configure(text="No. to Roll")

    def grid_set(self, *widgets: Widgets):
        "adds widgets to the grid"
        for w in widgets:
            match w:
                case Widgets.ROLL:
                    self.reroll.grid()
                    self.button_frame.grid()
                case Widgets.FORM:
                    self.gen_xls.grid()
                    self.get_path.grid()
                    self.num_pages_label.configure(text="No. Pages")


class MainPanel(ttk.Frame):
    "Main frame for the UI"
    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=5, width=WIDTH, height=HEIGHT, **kwargs)
        self.grid(column=0, row=0, sticky=(N, S, E, W))

        self.root = parent
        self._what = WhatPanel(self)
        self._page = PagePanel(self)
        self._result = ResultsPanel(self)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=4)

        self.ungrid_set(Widgets.ROLL, Widgets.FORM)

        self._try_load()

    def clipboard(self, out):
        "copy the results to the clipboard"
        self.root.clipboard_clear()  # clear the clipboard because we are setting its contents
        self.root.clipboard_append(out)

    def set_page(self, page):
        "set page contents"
        self._page.set_page(page)

    def set_formula(self, form):
        "set the formula to use"
        self._result.set_formula(form)

    def set_result(self, result: list):
        "set results contents"
        self._result.set_result(result)

    def ungrid_set(self, *widgets: Widgets):
        "pass to results to remove widgets from the grid"
        self._result.ungrid_set(*widgets)

    def grid_set(self, *widgets: Widgets):
        "pass to results to add widgets to the grid."
        self._result.grid_set(*widgets)

    def reroll(self):
        "calls reroll to populate results"
        self._result.do_reroll()

    def save(self):
        "saves the data to disk"
        try:
            with open(DATA, "wb") as f:
                d = self._what.get_what()
                data = {
                    "what_list": d[0],
                    "what_choices": d[1]
                }
                pickle.dump(data, f)
        except FileNotFoundError:
            pass

    def _try_load(self):
        "try to load data from the disk"
        try:
            with open(DATA, "rb", ) as f:
                data = pickle.load(f)
                self._what.set_what(data["what_list"], data["what_choices"])
        except FileNotFoundError:
            self._what.set_what(
                [dat.All_tables, dat.Maze_Rats_pages, dat.formulas],
                ["All tables", "Maze Rats pages", "Formulas"],
            )


class ListMaster:  # pylint: disable=too-many-instance-attributes
    """
    Tkinter UI for generating random choices, and creating tables and formulas.
    """
    def __init__(self, root):
        "Initializes the the UI; utilizes many helper functions"
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self._main = MainPanel(root)

    def on_close(self):
        "save before close"
        self._main.save()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ListMaster(root)
    root.mainloop()
