"the what panel: chooses what top level category to use."

import tkinter as tk
from tkinter import E, N, S, W, ttk

from enums import State, table
from gendata import Formula, MetaFormula
from ListPanel import ListPanel


class WhatPanel(ListPanel):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    "generates the What panel, for choosing what top level category to use"
    def __init__(self, parent: "MainPanel", **kwargs):
        super().__init__(parent, 0, **kwargs)
        self._parent: "MainPanel" = parent

        self.what_list: list[tuple[str, table]] = []
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))

        # radio button set
        self.mode_var = tk.StringVar()

        self.roll_mode_button = ttk.Radiobutton(
            self.button_frame,
            text="Dice tables",
            variable=self.mode_var,
            value=State.ROLL.value,
            command=self.set_mode
        )
        self.roll_mode_button.grid(column=0, row=0, sticky=(N, S, E, W))

        self.edit_mode_button = ttk.Radiobutton(
            self.button_frame,
            text="Add/Edit tables",
            variable=self.mode_var,
            value=State.EDIT.value,
            command=self.set_mode
        )
        self.edit_mode_button.grid(column=0, row=1, sticky=(N, S, E, W))

        self.mode_var.set(State.ROLL.value)

        self.add_button = ttk.Button(self.button_frame, text="New Category", command=self.add_cat)
        self.add_button.grid(column=1, row=0, sticky=(N, S, E, W))
        self.add_button.grid_remove()

        self.edit_button = ttk.Button(self.button_frame, text="Edit Category", command=self.edit_cat)
        self.edit_button.grid(column=1, row=1, sticky=(N, S, E, W))
        self.edit_button.grid_remove()

        self.rowconfigure(1, weight=1)

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=2)

    def accept_edit(self, newtext: str) -> bool:
        "Must be overridden to edit"

        if newtext == "":
            del self.choices[self.last_selection]
            del self.what_list[self.last_selection]
        elif self._is_safe(newtext):
            self.choices[self.last_selection] = newtext
            _, tab = self.what_list[self.last_selection]
            self.what_list[self.last_selection] = (newtext, tab)

    def set_what_data(self, lst: list[tuple[str, table]], choice: list[str]):
        "sets the values for the what panel, the list needs to have data in it, choice should have the labels."
        self.what_list = lst
        self.choices = choice
        self._update_lbox()

    def set_mode(self):
        "Tells the parent to set the mode"
        self._parent.set_state(State(self.mode_var.get()))

    def set_state(self):
        "set state handler called when _parent changes state"

        match self._parent.state:
            case State.ROLL:
                self.add_button.grid_remove()
                self.edit_button.grid_remove()
            case State.EDIT:
                self.add_button.grid()
                self.edit_button.grid()
            case _:
                pass

    def get_what(self) -> tuple[list[tuple[str, table]], list[str]]:
        "gets the top level what lists"
        return self.what_list, self.choices

    def do_lbox_sel(self, *args):  # pylint: disable=unused-argument
        "handles the 'what' column, which is the top level category, and fills out the page choices"
        if (sel := self._sel()) is not None:
            self._parent.set_page(self.what_list[sel])
            self._parent.set_result([])
            self._parent.set_item(("", []))

    def add_cat(self):
        "add a new category to the what panel"
        self.choices.append("")
        self.what_list.append(("",[]))
        self._update_lbox()
        self.last_selection = len(self.choices)-1
        self.lbox.activate(self.last_selection)
        return self._start_edit("")

    def edit_cat(self):
        "edit the name of a category on the what panel"
        if self.last_selection:  # we don't want to to edit the special all tables entry at 0,
            self.lbox.activate(self.last_selection)
            return self._start_edit(self.choices[self.last_selection])
        return "return"

    def add_to_all(self, tab: tuple[str, table]):
        "add a new table to the all list"
        # if not self._parent.has_name(tab[0]): # would be a double check our caller checks fairst
        self.what_list[0][1].append(tab)

    def rename(self, name: str, newname: str) -> bool:
        "renames a table"
        if self._parent.has_name(newname):
            return False

        for i, x in self.what_list[0]:
            if x[0] == name:
                match(x[1]):
                    case MetaFormula() | Formula():
                        x[1].name = newname
                    case _:
                        pass
                self.what_list[0][i] = (newname, x[1])
                return True

