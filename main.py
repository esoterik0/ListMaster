"the main panel: holds all the panels; main frame in root window"

from tkinter import E, N, S, W, ttk

import dill as pickle

import gendata as dat
from enums import HEIGHT, WIDTH, State, Widgets
from page import PagePanel
from results import ResultsPanel
from what import WhatPanel

DATA = "tables.dat"


class MainPanel(ttk.Frame):  # pylint: disable=too-many-ancestors
    "Main frame for the UI"
    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=5, width=WIDTH, height=HEIGHT, **kwargs)
        self.grid(column=0, row=0, sticky=(N, S, E, W))

        self.root = parent  # this is the same as something in super
        # all the panels of our application
        self._what = WhatPanel(self)  # A book, set, list, etc. A collection of rollables
        self._page = PagePanel(self)  # A page is a list of rollables
        self._result = ResultsPanel(self)  # this is the resulst of rolling the rollabable

        # our panel are arranged horizontally, in a single row.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=7)

        self.result_ungrid_set()

        self.state = State.ROLL
        self.widget = Widgets.ROLL
        self._data = DATA
        self.do_try_load()

    def set_state(self, state: State):
        "sets the internal state value to a state"
        self.state = state

        match state:
            case State.ROLL:
                self.widget = Widgets.ROLL
            case State.EDIT:
                self.widget = Widgets.EDIT

        for panel in [self._what, self._page, self._result]:
            panel.set_state()

    def get_data(self):
        "get the current file name"
        return self._data

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

    def result_ungrid_set(self):
        "pass to results to remove widgets from the grid"
        self._result.ungrid_set()

    def result_grid_set(self, widget: Widgets):
        "pass to results to add widgets to the grid."
        self._result.grid_set(widget)

    def what_ungrid_set(self):
        "pass to results to remove widgets from the grid"
        self._what.ungrid_set()

    def what_grid_set(self, widget: Widgets):
        "pass to results to add widgets to the grid."
        self._what.grid_set(widget)

    def set_data(self, data):
        "sets the data filename"
        if data:
            self._data = data
        else:
            self._data = DATA

    def reroll(self):
        "calls reroll to populate results"
        self._result.do_reroll()

    def save(self):
        "saves the data to disk"
        try:
            with open(self._data, "wb") as f:
                d = self._what.get_what()
                data = {
                    "what_list": d[0],
                    "what_choices": d[1]
                }
                pickle.dump(data, f)
        except FileNotFoundError:
            pass

    def do_try_load(self):
        "try to load data from the disk"
        try:
            with open(self._data, "rb", ) as f:
                data = pickle.load(f)
                self._what.set_what(data["what_list"], data["what_choices"])
        except FileNotFoundError:
            self.do_reset()
            return

        self._page.set_page([])
        self._result.set_result([])

    def do_reset(self):
        "perform a reset of the data to the hardcoded values"
        self._what.set_what(
            [dat.All_tables, dat.Maze_Rats_pages, dat.formulas],
            ["All tables", "Maze Rats pages", "Formulas"],
        )

        self._page.set_page([])
        self._result.set_result([])

    def do_import(self, file):
        "Import and merge lists"
        wlist, wchoices = self._what.get_what()

        data = None
        try:
            with open(file, "rb", ) as f:
                data = pickle.load(f)
        except FileNotFoundError:
            return

        append = []  # values to add after combining choices with the same name

        # merge existing lists and track new choices to append.
        for fob, choice in zip(data["what_list"], data["what_choices"]):
            try:
                # if the choice exists merge the lists
                wlist[wchoices.index(choice)] += fob
            except ValueError:
                # if the choice is new add it after this loop.
                append.append((choice, fob))

        # add new choices
        for choice, fob in append:
            wlist.append(fob)
            wchoices.append(choice)

        # set the choices.
        self._what.set_what(wlist, wchoices)

    def do_clear(self):
        "Clear all data"

        # we always need an all tables entry.
        self._what.set_what(
            [[]],
            ["All tables"],
        )

        self._page.set_page([])
        self._result.set_result([])
