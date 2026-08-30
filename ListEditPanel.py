"Panel for editing list items, with an editable title at the top of the listbox"

import tkinter as tk
from tkinter import E, N, S, W, ttk

from ListPanelABC import ListPanelABC


class ListEditPanel(ListPanelABC):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    """
    Panel for editing list items, with an editable title at the top of the listbox
    """
    def __init__(self, parent, root: tk.Tk | tk.Toplevel, **kwargs):
        super().__init__(parent, **kwargs)

        # setup title label, stringvar to control it, and validation.
        self.title_val = (root.register(self._is_safe), "%P")
        self.title_var = tk.StringVar()
        self.title = ttk.Entry(
            self,
            textvariable=self.title_var,
            validate="key",
            validatecommand=self.title_val
        )
        self.title.grid(column=0, row=self.TOP_ROW, sticky=(N, S, E, W))
        self.title_var.set("Title")

        self.lbox.bind("<Delete>", self.remove)
        self.lbox.bind("<BackSpace>", self.remove)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=self.ROW, sticky=(E, W))
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)

        self.add_item_button = ttk.Button(
            self.button_frame,
            text="add item",
            command=self.add_item
        )
        self.add_item_button.grid(row=0,column=0,sticky=(N, S, E, W))

        self.lbox.bind("<Double-1>", self.edit_cat)

    def remove(self, *args): # plint: disable=W0613
        "remove an entry"
        if self.last_selection is not None:
            del self.choices[self.last_selection]
            self.update_lbox()

    def accept_edit(self, newtext: str) -> bool:
        "verify accept and execute edit"

        if newtext == "":
            del self.choices[self.last_selection]
            self.update_lbox()
            return True

        if self._is_safe(newtext):
            self.choices[self.last_selection] = newtext
            self.update_lbox()
            return True

        return False

    def do_lbox_sel(self, *args):  # pylint: disable=W0613
        "called when the listbox selection changes"
        self._sel()

    def edit_cat(self, *args):  # pylint: disable=W0613
        "edit the selected category"
        if self._sel() is not None:
            return self._start_edit(self.choices[self.last_selection])

        return "continue"

    def add_item(self):
        "add item"
        self.choices.append("")
        self.update_lbox()
        self.last_selection = len(self.choices)-1
        self.look()
        return self._start_edit("")
