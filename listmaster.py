"listmaster.py: roll on random tables; create and edit random tables;"

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from main import MainPanel


class ListMaster:  # pylint: disable=too-many-instance-attributes
    """
    Tkinter UI for generating random choices, and creating tables and formulas.
    """
    def __init__(self, root):
        "Initializes the the UI; utilizes many helper functions"
        self.root = root
        self.root.option_add('*tearOff', False)  # disable obsolete default ui setting
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # handle close messages
        self.root.title("List Master")  # set's main (root) menu title

        # menu setup
        # -| menu bar (root)
        #  |- File
        #   |- Commands
        self.menu = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu)
        # self.import_menu = tk.Menu(self.menu)
        # add commands
        self.file_menu.add_command(label="New / Clear data", command=self.on_new)
        self.file_menu.add_command(label="Reset to defaults", command=self.on_reset)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Load", command=self.on_load)  # Replaces the data
        self.file_menu.add_command(label="Import", command=self.on_import)  # Adds the the data
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save", command=self.on_save)  # Save over the current file
        self.file_menu.add_command(label="Save as", command=self.on_save_as)  # Save to a New file
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save & Quit", command=self.on_close)
        self.file_menu.add_command(label="Just Quit (No prompt)", command=self.on_quit)
        self.menu.add_cascade(menu=self.file_menu, label="File")  # put file menu in root
        # self.import_menu.add_command(label="Import list (pdf)", command=self.on_import_pdf)
        # self.import_menu.add_command(label="Import list (txt)", command=self.on_import_txt)
        # self.menu.add_cascade(menu=self.import_menu, label="Import")  # put import menu in root
        self.root["menu"] = self.menu  # set root menu

        # we configure root to only have one grid square our applincation will add
        # a single panel that contains all the application UI.
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Main Panel is our single panel application.
        self._main = MainPanel(self.root)

    def get_path_file(self):
        "gets the path and filename of the current file to save"
        path = os.getcwd()
        file = self._main.get_data()

        if x := max(file.rfind('/'), file.rfind('\\')) >= 0:
            path = file[0:x]
            file = file[x+1:]

        return path, file

    def on_save(self):
        "Saves data to the last used filename"
        self._main.save()

    def on_save_as(self):
        "Saves data to a file, asks for name"
        path, file = self.get_path_file()
        self._main.set_data(
            filedialog.asksaveasfilename(
                initialdir=path,
                initialfile=file,
                defaultextension=".dat"
            )
        )
        self._main.save()

    def on_quit(self):
        "Quit without saving or prompting"
        self.root.destroy()  # Quit

    def on_close(self):
        "handle the close action; save before close"
        code = messagebox.askyesnocancel(
            message="Do you want to Save?\n\n"
                    "Yes:\tSave & Quit\n"
                    "No:\tJust Quit\n"
                    "Cancel:\tDon't Quit",
            title="Save & Quit?"
        )

        if code is None:  # Cancel
            return  # don't quit

        if code:  # Yes
            self._main.save()  # Save & Quit

        self.root.destroy()  # No / Just Quit

    def on_reset(self):
        "resets to hardcoded values"
        self._main.do_reset()

    def on_new(self):
        "clears all data creating a new clean setup"
        self._main.do_clear()

    def on_load(self):
        "loads data from a file"
        path, file = self.get_path_file()
        self._main.set_data(
            filedialog.askopenfilename(
                initialdir=path,
                initialfile=file,
                defaultextension=".dat"
            )
        )

        self._main.do_try_load()

    def on_import(self):
        "Imports and merges data from a file"
        path, file = self.get_path_file()
        self._main.do_import(
            filedialog.askopenfilename(
                initialdir=path,
                initialfile=file,
                defaultextension=".dat"
            )
        )

    # def on_import_pdf(self):
    # def on_import_txt(self):
