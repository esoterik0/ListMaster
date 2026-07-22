"ListPanel: abstract base class for lists with inplace editing"

import re
import tkinter as tk
from tkinter import E, N, S, W, ttk
from typing import Literal
import AutoScrollBar

from enums import HEIGHT, WIDTH

ROW = 0

class ListPanel(ttk.Frame):  # pylint: disable=too-many-ancestors,too-many-instance-attributes,invalid-name
    """
    Abstract base class ListPanel has:
        a list box, and behavior for a sublasses to use
        .safe() - a regex check for safe text
        inplace edditing
        drag and drop reordering
    Subclasses must implement:
        do_lbox_sel() - called when the listbox selection changes
        accept_edit() - called when an inplace edit is accepted
    Subclasses may implement:
        cancel_edit() - called when an inplace edit is canceled
        drag() - called when a drag and drop reordering is completed
    """
    TITLE_ROW = 0
    OUR_ROW = 1
    ROW = OUR_ROW + 2
    def __init__(self, parent, column, drag=False, **kwargs):
        "initialize parent frame and grid ouselves"
        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=column, row=0, sticky=(N, S, E, W))
        self.last_selection = None
        self.edit = None  # to allow out of band exit, i.e. .widget.destroy()
        # safe text pattern we want to preserve ';{}`' for delimiter use
        self.safepat = re.compile(r"[\w,|&:+()\[\] ]+")
        self.drag_start = None

        self.title_var = tk.StringVar()
        self.title = ttk.Label(self, textvariable=self.title_var, anchor="center")
        self.title.grid(column=0, row=self.TITLE_ROW, sticky=(N, S, E, W))
        self.title_var.set("Title")

        # listbox choices
        self.choices: list[str] = []
        self.choice_var = tk.StringVar()

        # listbox
        self.lbox = tk.Listbox(self, listvariable=self.choice_var, width=int(WIDTH/5), height=HEIGHT)
        self.lbox.grid(column=0, row=self.OUR_ROW, sticky=(N, S, E, W))
        self.lbox.bind("<<ListboxSelect>>", self._do_lbox_sel)

        if drag: # we only bind drag events if we are a drag enabled listbox
            self.lbox.bind("<ButtonPress-1>", self._drag_begin)
            self.lbox.bind("<ButtonRelease-1>", self._drag_end)

        # scroll bars for listbox # no easy way to hide when not needed (subclass overide disable?)
        # it might be possible to hook when the scrollbars change, and see if they need to be degridded?
        self.scrolly = AutoScrollBar.AutoScrollBar(self, command=self.lbox.yview)
        self.lbox.configure(yscrollcommand=self.scrolly.set)
        self.scrolly.grid(row=self.OUR_ROW, column=1, sticky=(N, S))

        self.scrollx = AutoScrollBar.AutoScrollBar(self, orient="horizontal", command=self.lbox.xview)
        self.lbox.configure(xscrollcommand=self.scrollx.set)
        self.scrollx.grid(row=self.OUR_ROW+1, column=0, sticky=(E, W))

        #configure ourselves
        self.rowconfigure(self.OUR_ROW, weight=1)
        # self.rowconfigure(self.ROW, weight=1)
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
        if len(sel) == 1:
            self.last_selection = sel[0]
            return self.last_selection
        return None

    def _do_lbox_sel(self, *args):
        self.do_lbox_sel(*args)

    def _drag_begin(self, e):
        "begin a drag"
        # x, y = e.x, e.y
        self.drag_start = self.lbox.index(f"@{e.x},{e.y}")

    def _drag_end(self, e):
        "end drag"
        # x, y = e.x, e.y
        end = self.lbox.index(f"@{e.x},{e.y}")

        if self.drag_start is not None and end is not None:
            self.drag(self.drag_start, end)

    def drag(self, start, end):
        "does completes the drag, may be overridden"
        l = len(self.choices)
        if start >= l or end >= l or start < 0 or end < 0:
            return

        # swap them
        self.choices[start], self.choices[end] = self.choices[end], self.choices[start]
        self._update_lbox()

    def look(self):
        "activates and scrolls to the last selection"
        self.lbox.activate(self.last_selection)
        self.lbox.see(self.last_selection)

    def do_lbox_sel(self, *args):
        "Must be overridden by subclass; subclasses have different behavior."
        raise NotImplementedError

    def accept_edit(self, newtext: str) -> bool:
        "Must be overridden to edit; subclasses have different behavior."
        raise NotImplementedError

    def cancel_edit(self):
        "override to add behavior on cancel"

    def _is_safe(self, newtext: str) -> bool:
        "returns true if the text is 'safe'"
        mat = self.safepat.fullmatch(newtext)
        return mat is not None

    # optional string instead of looking up by index
    def _start_edit(self, text: str | None = None) -> Literal["break"]:
        "start an in place edit for an item in our list box"
        #assert(self.last_selection is not None)
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
        self.edit = None

    def _cancel_edit(self, event):
        "cancel an in place edit"
        self.cancel_edit()
        event.widget.destroy()  # close edit
        self.edit = None
