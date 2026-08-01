"module window/dialog, to import a text file"

import tkinter as tk
from tkinter import E, N, S, W, messagebox, ttk

from import_base import import_base
from ListEditPanel import ListEditPanel
from PanelCom import PanelCom


class import_txt(import_base):  # pylint: disable=too-many-instance-attributes
    "window/dialog to import a text file"
    def __init__(self, parent, file, panel: PanelCom, **kw_args):
        super().__init__(parent, **kw_args)
        self.panel: PanelCom = panel
        self.filename = file
        self.lstpan: ListEditPanel | None = None
        self.list_width = 40
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        # self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.grid(row=0, column=0, sticky=(N, E, W))

        self.file_label = tk.Label(self.button_frame, text=f"File name: {file}")
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
        title, _, _ = self._get_title_path_ext_from_file(self.filename)
        if self.lstpan is not None:
            self.lstpan.grid_remove()
            self.lstpan.destroy()


        with open(self.filename, "r", encoding="utf-8") as f:
            lst = f.readlines()

        lst = self._filter_list(lst)
        self.lstpan = ListEditPanel(self.frame, self.winfo_toplevel())
        #self.frame.columnconfigure(1, weight=1)
        self.lstpan.grid(row=0, column=1)
        self.lstpan.title_var.set(title)
        self.lstpan.choices = lst

        self.lstpan.update_lbox()

    def save(self):
        "save the list"

        if not self.lstpan:
            messagebox.showerror(
                message="No tables found to save.\nClose the window to exit.",
                title="Tables have not been parsed"
            )  # consider merging the tables.
            return

        self.panel.insert_new_table(self.lstpan.title_var.get(), self.lstpan.choices)

        self.destroy()
