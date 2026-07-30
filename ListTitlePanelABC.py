"Abstract base class for list-title panels."

import tkinter as tk
from tkinter import E, N, S, W, ttk

from ListPanelABC import ListPanelABC


class ListTitlePanelABC(ListPanelABC):  # pylint: disable=too-many-ancestors,too-many-instance-attributes,invalid-name,abstract-method
    """
    Abstract base class for list-title panels in the list application.
    adds a title label to the top of the listbox, and a title_var StringVar to control it.

    like our parent class ListPanelABC, this class is intended to be subclassed.
    Subclasses must implement:
        do_lbox_sel() - called when the listbox selection changes
        accept_edit() - called when an inplace edit is accepted
    Subclasses may implement:
        cancel_edit() - called when an inplace edit is canceled
        drag() - called when a drag and drop reordering is completed
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # setup title label and stringvar to control it.
        self.title_var = tk.StringVar()
        self.title = ttk.Label(self, textvariable=self.title_var, anchor="center")
        self.title.grid(column=0, row=self.TOP_ROW, sticky=(N, S, E, W))
        self.title_var.set("Title")
