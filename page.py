"the page panel: shows what pages are in the top level category chosen by the what panel."

import tkinter as tk
from tkinter import E, N, S, W, ttk

from enums import HEIGHT, WIDTH, State


class PagePanel(ttk.Frame):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    "generates the page frame, for choosing, inspecting, or editing which 'page', formula or table"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=1, row=0, sticky=(N, S, E, W))
        self._parent = parent
        self.last_selection = None

        self.page_choices = tk.StringVar()

        self._page = tk.Listbox(self, listvariable=self.page_choices, width=int(3*WIDTH/5), height=HEIGHT)
        self._page.grid(column=0, row=0, sticky=(N, S, E, W))
        self._page.bind("<<ListboxSelect>>", self.do_page)
        self._page.bind("<Double-1>", self.do_double_page)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))
        self.button_frame.grid_remove()

        self.new_form = ttk.Button(self.button_frame, text="New Form", command=self.do_new_form, default='disabled')
        self.new_form.grid(column=0, row=1, sticky=(N, S, E, W))
        self.new_list = ttk.Button(self.button_frame, text="New List", command=self.do_new_list)
        self.new_list.grid(column=0, row=0, sticky=(N, S, E, W))
        self.add_item = ttk.Button(self.button_frame, text="Add Item", command=self.do_add_item)
        self.add_item.grid(column=1, row=0, sticky=(N, S, E, W))
        self.edit_item = ttk.Button(self.button_frame, text="Edit Item", command=self.do_edit_item)
        self.edit_item.grid(column=1, row=0, sticky=(N, S, E, W))

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._cur_page = None

    def set_page(self, lst: list | None):
        "sets the contents of the page panel"
        self._cur_page = lst
        self.page_choices.set([n for n, _ in self._cur_page])
        self.grid_set()

    def _sel(self) -> bool:
        "handle selections"
        sel = self._page.curselection()
        if len(sel) == 1:
            self.last_selection = sel[0]
            return True
        return False

    def do_page(self, *args):  # pylint: disable=unused-argument
        "handles the 'page' column to choose which table, page, or formula to generate from; triggers re-roll"
        if not self._cur_page:
            return

        if self._sel():
            if self._parent.state == State.ROLL:
                self._parent.set_item(self._cur_page[self.last_selection])

    def do_double_page(self, e):  # pylint: disable=unused-argument
        "handles double click on the 'page' column to choose what to edit"
        if not self._cur_page:
            return

        if self._sel():
            if self._parent.state == State.EDIT:
                self.do_edit_item()

    def do_edit_item(self):
        "handle edit item button, and double click"
        if not self._cur_page:
            return

        if self.last_selection is not None:
            if self._parent.state == State.EDIT:
                self._parent.set_item(self._cur_page[self.last_selection])

    def ungrid_set(self):
        "removes widgets"
        self.button_frame.grid_remove()

    def grid_set(self):
        "adds widgets"
        if self._parent.state == State.EDIT:
            self.button_frame.grid()

    def set_state(self):
        "set state handler called when _parent changes state"
        self.ungrid_set()
        self._cur_page = None
        self.page_choices.set([])
        self.grid_set()

    def do_new_form(self):
        "handle new Form button"

    def do_new_list(self):
        "handle new list button"

    def do_add_item(self):
        "handle add item button"
