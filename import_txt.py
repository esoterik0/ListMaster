"module window/dialog, to import a list from text file"

import tkinter as tk
from tkinter import E, N, W, ttk

from import_base import import_base
from ListEditPanel import ListEditPanel
from PanelCom import PanelCom


class import_txt(import_base):  # pylint: disable=too-many-instance-attributes
    "window/dialog to import a list from text file"
    def __init__(self, parent, file, panel: PanelCom, **kw_args):
        super().__init__(parent, **kw_args)
        self.panel: PanelCom = panel
        self.filename = file
        self.lstpan: ListEditPanel | None = None

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.grid(row=0, column=0, sticky=(N, E, W))

        self.file_label = tk.Label(self.button_frame, text=f"File: {file}")
        self.file_label.grid(row=0, column=0, sticky=(E, W))

        self.save_button = ttk.Button(
            self.button_frame,
            text="save tables",
            command=self.save
        )
        self.save_button.grid(row=1, column=0, sticky=(E, W))

        self.parse()

    def parse(self):
        "parse the text file and make tables"
        title, _, _ = self._get_title_path_ext_from_file()

        lst: list[str]
        with open(self.filename, "r", encoding="utf-8") as f:
            lst = f.readlines()

        self.lstpan = ListEditPanel(self.frame, self.winfo_toplevel())
        self.lstpan.grid(row=0, column=1)
        self.lstpan.title_var.set(title)
        self.lstpan.choices = self._filter_list(lst)

        self.lstpan.update_lbox()

    def save(self):
        "save the list"

        if self.lstpan:
            if self.panel.insert_new_table(
                self.lstpan.title_var.get()[:self.Title_Len],
                self.lstpan.choices
            ):
                self.destroy()
