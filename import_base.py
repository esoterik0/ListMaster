"module window/dialog, to import a text file"

import re
import tkinter as tk
from tkinter import E, N, S, W, ttk


class import_base(tk.Toplevel):
    "base class for importing has common functions"
    def __init__(self, parent, **kw_args):
        super().__init__(parent, **kw_args)

        self.Title_Len = 60
        self.filename = ""

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.frame =  ttk.Frame(self)
        self.frame.grid(row=0, column=0, sticky=(E, N, S, W))

        # re to cut the numbers from the begining of the line
        self.numcut = re.compile(r"^[\d\.\,\;\:]+")  # ^ to garantee we only match at the start of the string.

        # setup modal dialog
        self.wait_visibility() # this is needed apparently
        self.transient(parent) # informs modal behavior
        self.protocol('WM_DELETE_WINDOW', self.grab_release()) # release modal behavior on close
        self.grab_set() # start modal behavior

    ###########################################################################
    # helpers

    def _filter_list(self, lst: list[str]) -> list[str]:
        "filters a table to remove empty lines and leading numbers"
        lst = ["".join([y.strip() for y in self.numcut.split(x)]) for x in lst]  # remove leading numbers
        lst = [x for x in lst if x]  # remove empty strings
        return lst

    def _get_title_path_ext_from_file(self) -> tuple[str, str, str]:
        "gets the title from a filename"
        path = ""
        fname = self.filename
        if (x := max(fname.rfind('/'), fname.rfind('\\'))) >= 0:
            path = fname[0:x]
            fname = fname[x+1:]

        ext = ""
        if (x := fname.rfind('.')) >= 0:
            ext = fname[x+1:]
            fname = fname[0:x]

        return fname, path, ext

