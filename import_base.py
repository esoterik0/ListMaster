"module window/dialog, to import a text file"

import re
import tkinter as tk
from enum import Enum

class ListType(Enum):
    "list type single or multiple"
    SINGLE = 1
    MULTI = 2


class TitleType(Enum):
    "what is the title delim"
    SAME=0
    DIFF=1
    NONE=2
    FILE=3
    MISS=4


class import_base(tk.Toplevel):
    "base class for importing has common functions"
    def __init__(self, parent, **kw_args):
        super().__init__(parent, **kw_args)

        self.numcut = re.compile(r"^[\d\.\,\;\:]+")  # ^ to garantee we only match at the start of the string.
        self.wait_visibility()
        self.protocol('WM_DELETE_WINDOW', self.grab_release())
        self.grab_set()
        self.transient(parent)

    def _filter_list(self, lst: list[str]) -> list[str]:
        "filters a table to remove empty lines and leading numbers"
        lst = [self.numcut.split(x)[1].strip() for x in lst]
        lst = [x for x in lst if x]  # remove empty strings
        return lst

    def _get_title_path_ext_from_file(self, fname: str) -> tuple[str, str, str]:
        "gets the title from a filename"
        path = ""
        if (x := max(fname.rfind('/'), fname.rfind('\\'))) >= 0:
            path = fname[0:x]
            fname = fname[x+1:]

        ext = ""
        if (x := fname.rfind('.')) >= 0:
            ext = fname[x+1:]
            fname = fname[0:x]

        return fname, path, ext