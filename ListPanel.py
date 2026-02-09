"ListPanel: abstract base class for lists with inplace editing"

import re
import tkinter as tk
from tkinter import E, N, S, W, ttk
from typing import Literal

from enums import HEIGHT, WIDTH


class ListPanel(ttk.Frame):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    "Abstract base class, ListPanel has a list box, and inplace edditing available"
    def __init__(self, parent, column, **kwargs):
        # initialize parent frame and grid ouselv
        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=column, row=0, sticky=(N, S, E, W))
        self.last_selection = None
        self.edit = None  # to allow out of band exit.
        self.safepat = re.compile(r"[\w ]*")  # safe text pattern

        # listbox choices
        self.choices: list[str] = []
        self.choice_var = tk.StringVar()

        # listbox
        self.lbox = tk.Listbox(self, listvariable=self.choice_var, width=int(WIDTH/5), height=HEIGHT)
        self.lbox.grid(column=0, row=0, sticky=(N, S, E, W))
        self.lbox.bind("<<ListboxSelect>>", self.do_lbox_sel)

        # scroll bar fol listbox # no easy way to hide when not needed (subclass overide disable?)
        self.scroll = ttk.Scrollbar(self, command=self.lbox.yview)
        self.lbox.configure(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=0, column=1, sticky=(N, S))

        #configure ourselves
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _update_lbox(self):
        """
        Updates the what_choice_var to self.choices
        should be called by subclasses to update self.choice_var
        """
        self.choice_var.set(self.choices)

    def _sel(self):
        "current->last selection logic; helper function"
        sel = self.lbox.curselection()
        self.last_selection = sel[0] if len(sel) == 1 else None
        return self.last_selection

    def do_lbox_sel(self, *args):
        "Must be overridden by subclass; subclasses have different behavior."
        raise NotImplementedError

    def accept_edit(self, newtext: str) -> bool:
        "Must be overridden to edit; subclasses have different behavior."
        raise NotImplementedError

    def _is_safe(self, newtext: str) -> bool:
        "returns true if the text is 'safe'"
        return bool(self.safepat.match(newtext).group())

    def _start_edit(self, text: str | None = None) -> Literal["break"]: # optional string instead of looking up by index
        "start an in place edit for an item in our list box"
        if text is None:
            text = self.lbox.get(self.last_selection)

        entry = tk.Entry(self.lbox, borderwidth=0, highlightthickness=1)
        self.edit = entry # allow's external cancelation

        entry.bind("<Return>", self._accept_edit)
        entry.bind("<Escape>", self._cancel_edit)

        entry.insert(0, text)
        entry.selection_from(0)
        entry.selection_to("end")
        entry.place(relx=0, y=self.lbox.bbox(self.last_selection)[1], relwidth=1, width=-1)
        entry.focus_set()
        entry.grab_set()

        return "break"

    def _accept_edit(self, event):
        "accept and finish an in place edit"
        self.accept_edit(event.widget.get())  # subclass accept
        event.widget.destroy()  # close edit
        self._update_lbox()  # update the listbox

    def _cancel_edit(self, event):
        "cancel an in place edit"
        event.widget.destroy()  # close edit
