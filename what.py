"the what panel: chooses what top level category to use."

import tkinter as tk
from tkinter import E, N, S, W, ttk

from enums import HEIGHT, WIDTH, Widgets, State


class WhatPanel(ttk.Frame):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
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

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))

        self.mode_var = tk.StringVar()

        self.roll_mode_button = ttk.Radiobutton(
            self.button_frame,
            text="Dice tables",
            variable=self.mode_var,
            value=State.ROLL.value,
            command=self.set_mode
        )
        self.edit_mode_button = ttk.Radiobutton(
            self.button_frame,
            text="Add/Edit tables",
            variable=self.mode_var,
            value=State.EDIT.value,
            command=self.set_mode
        )

        self.add_button = ttk.Button(self.button_frame, text="New Category", command=self.add_cat)
        self.add_button.grid(column=1, row=0, sticky=(N, S, E, W))
        self.add_button.grid_remove()

        self.mode_var.set(State.ROLL.value)

        self.roll_mode_button.grid(column=0, row=0, sticky=(N, S, E, W))
        self.edit_mode_button.grid(column=0, row=1, sticky=(N, S, E, W))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=2)

    def set_what(self, lst, choice):
        "sets the values for the what panel, the list needs to have data in it, choice should have the labels."
        self.what_list = lst
        self.choices = choice
        self.what_choice_var.set(choice)

    def set_mode(self):
        "Tells the parent to set the mode"
        match self.mode_var.get():
            case State.ROLL.value:
                self._parent.set_state(State.ROLL)
            case State.EDIT.value:
                self._parent.set_state(State.EDIT)

    def get_what(self) -> tuple[list, list]:
        "gets the top level what lists"
        return self.what_list, self.choices

    def do_what(self, *args):  # pylint: disable=unused-argument
        "handles the 'what' column, which is the top level category, and fills out the page choices"
        sel = self.what.curselection()

        if len(sel) == 1:
            self._parent.set_page(self.what_list[sel[0]])
            self._parent.set_result([])
            self._parent.result_ungrid_set()

    def set_state(self):
        "set state handler called when _parent changes state"

        self.ungrid_set()
        self.grid_set(self._parent.widget)

    def ungrid_set(self):
        "removes widgets from the grid"
        self.button_frame.grid_remove()

    def grid_set(self, widget: Widgets):
        "adds widgets to the grid"

        self.button_frame.grid()
        match widget:
            case Widgets.ROLL:
                self.add_button.grid_remove()
            case Widgets.EDIT:
                self.add_button.grid()

    def add_cat(self):
        "add a new category to the what panel"
