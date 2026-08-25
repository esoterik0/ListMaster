"the what panel: chooses what top level category to use."

import tkinter as tk
from tkinter import E, N, S, W, messagebox, ttk

from enums import State, table
from gendata import Formula, MetaFormula
from ListTitlePanelABC import ListTitlePanelABC
from PanelCom import PanelCom


class WhatPanel(ListTitlePanelABC):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    "generates the What panel, for choosing what top level category to use"
    def __init__(self, parent: PanelCom, **kwargs):
        super().__init__(parent, drag=True, **kwargs)
        self._parent: PanelCom = parent
        self.what_list: list[tuple[str, table]] = []
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=self.ROW, sticky=(E, W))

        self.lbox.bind("<Double-1>", self.edit_cat)
        self.lbox.bind("<F2>", self.edit_cat)

        self.title_var.set("What")

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
        self.edit_mode_button.grid(column=1, row=0, sticky=(N, S, E, W))

        self.mode_var.set(State.ROLL.value)

        self.add_button = ttk.Button(self.button_frame, text="New Category", command=self.add_cat)
        self.add_button.grid(column=0, row=2, sticky=(N, S, E, W))
        self.add_button.grid_remove()

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

    def accept_edit(self, newtext: str) -> bool:
        "verify accept and execute edit"

        if self.last_selection is None:
            return

        if newtext == "":
            if bool( # bool may not be needed could use == True, which is basically the same
                messagebox.askyesnocancel(
                    message="Are you sure you want to DELETE",
                    title="Are you sure?"
                )
            ):
                del self.choices[self.last_selection]
                del self.what_list[self.last_selection]
                return

        if self._is_safe(newtext):
            self.choices[self.last_selection] = newtext

    def cancel_edit(self):
        "override to add behavior on cancel"
        # this should only trigger when canceling a new category; we should never have an empty string
        # in the list unless a new category was canceled
        if self.last_selection is None:
            return

        if self.choices[self.last_selection] == "":
            del self.choices[self.last_selection]
            del self.what_list[self.last_selection]
            self.last_selection = None

    def set_what_data(self, lst: list[tuple[str, table]], choice: list[str]):
        """
        sets the values for the what panel,
        the list needs to have data in it, (all tables at 0 minimum)
        choice should have the labels.
        """
        self.what_list = lst
        self.choices = choice
        self.last_selection = None
        self.update_lbox()

    def set_mode(self):
        "Tells the parent to set the mode, and update siblings"
        self._parent.set_state(State(self.mode_var.get()))

    def set_state(self):
        "set state handler called when _parent changes state"

        match self._parent.state:
            case State.ROLL:
                self.add_button.grid_remove()
            case State.EDIT:
                self.add_button.grid()
            case _:
                pass

    def drag(self, start, end):
        "override do not move all tables entry"
        # swap them
        if start == end:
            return

        if self._parent.state != State.EDIT:
            return

        if start == 0 or end == 0:
            return

        l = len(self.choices)
        if start >= l or end >= l:
            return

        # swap them
        self.choices[start], self.choices[end] = self.choices[end], self.choices[start]
        self.what_list[start], self.what_list[end] = self.what_list[end], self.what_list[start]
        self.update_lbox()

    def get_what(self) -> tuple[list[tuple[str, table]], list[str]]:
        "gets the top level what lists"
        return self.what_list, self.choices

    def do_lbox_sel(self, *args):  # pylint: disable=unused-argument
        "handles the 'what' column, which is the top level category, and fills out the page choices"

        # zero is allowed, so we need to check for None, not False
        if (sel := self._sel()) is not None:
            self._parent.set_page(self.choices[sel], self.what_list[sel])

            # clear results if we are in the roll state
            if self._parent.state == State.ROLL:
                self._parent.set_result_item()

    def add_cat(self):
        "add a new category to the what panel"
        self.choices.append("")
        self.what_list.append([])
        self.update_lbox()
        self.last_selection = len(self.choices)-1
        self.look()
        return self._start_edit("")

    def edit_cat(self, *args): # pylint: disable=W0613
        "edit the name of a category on the what panel"

        if self._parent.state != State.EDIT:
            return "continue"

        if self._sel():  # we don't want to to edit the special all tables entry at 0,
            self.lbox.activate(self.last_selection)
            self.lbox.see(self.last_selection)
            return self._start_edit(self.choices[self.last_selection])
        return "break"

    def add_to_all(self, tab: tuple[str, table]):
        "add a new table to the all list"
        if not self._is_safe(tab[0]):
            return False

        if not self._parent.has_name(tab[0]):
            self.what_list[0].append(tab)
            return True

        return False

    def add_to_cur(self, tab: tuple[str, table]):
        "add a new table to the current list and the all list"
        if not self._is_safe(tab[0]):
            messagebox.showerror(
                title="Invalid Characters",
                text="Your title has illegal characters in it"
            )
            return False

        if not self._parent.has_name(tab[0]):
            self.what_list[0].append(tab)
            if self.last_selection: #ignore 0 and None
                self.what_list[self.last_selection].append(tab)
                self._parent.set_page(  # reload the current page with the new table added
                    self.choices[self.last_selection],
                    self.what_list[self.last_selection]
                )
            return True

        messagebox.showerror(
            title="Name collision",
            text="You have chosen a name that already exists"
        )
        return False

    def delete_from_all(self, name):
        "delete from all tables, and all other tables"
        for j, lst in enumerate(self.what_list):
            for i, x in enumerate(lst):
                if x[0] == name:
                    del self.what_list[j][i]
                    break

    def rename(self, name: str, newname: str):
        "renames a table in the all list"
        if self._parent.has_name(newname):
            return

        for j, lst in enumerate(self.what_list):
            for i, x in enumerate(lst):
                if x[0] == name:
                    match(x[1]):
                        case MetaFormula() | Formula():
                            x[1].name = newname
                    self.what_list[j][i] = (newname, x[1])
                    break
