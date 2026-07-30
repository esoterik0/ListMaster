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

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=self.ROW, sticky=(E, W))

        self.lbox.bind("<Double-1>", self.edit_cat)

    def accept_edit(self, newtext: str) -> bool:
        "verify accept and execute edit"
        if self._is_safe(newtext):
            self.choices[self.last_selection] = newtext
            self.update_lbox()

            return True

        return False

    def do_lbox_sel(self, *args):
        "called when the listbox selection changes"
        self._sel()

    def edit_cat(self, event = None):
        "edit the selected category"
