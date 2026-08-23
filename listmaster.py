"""listmaster.py: manage random tables (lists)
    roll on random tables, formulas and metaformulas.
    save set of table
    load set of tables
    import set of tables
    create random tables.
    create random formulas; a set of tables to roll at once.
    +create random metaformulas; a table of similar formulas to choose from.
    edit random tables.
    import tables from pdf.
    import tables from txt.
    export table to txt.
"""

import os
import tkinter as tk
from tkinter import filedialog, font, messagebox

from enums import MENUSIZE, TEXTSIZE
from main import MainPanel


class ListMaster:  # pylint: disable=too-many-instance-attributes
    """
    Tkinter UI for ListMaster.

    Contains menu, and application level controls.
    Contains A single main panel (main.py) that controls the application logic
    """
    def __init__(self, root: tk.Tk):
        "Initializes the the UI (tk)"
        self.root: tk.Tk = root  # inject our root so that main (start.py) can control the flow
        self.root.option_add('*tearOff', False)  # disable obsolete default ui setting
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # handle close messages
        self.root.title("List Master")  # set's main (root) menu title

        # menu setup
        # -| menu bar (root)
        #  |- File
        #   |- Commands
        #  |- Import
        #   |- Commands
        self.menu = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu)
        # add commands
        self.file_menu.add_command(label="New / Clear data", command=self.on_new)
        self.file_menu.add_command(label="Reset to defaults", command=self.on_reset)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Load", command=self.on_load)  # Replaces the data
        self.file_menu.add_command(label="Import Database", command=self.on_import)  # Adds the the data
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save", command=self.on_save)  # Save over the current file
        self.file_menu.add_command(label="Save as", command=self.on_save_as)  # Save to a New file
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save & Quit", command=self.on_save_quit)
        self.file_menu.add_command(label="Just Quit (No prompt)", command=self.on_quit)
        self.menu.add_cascade(menu=self.file_menu, label="File")  # put file menu in root
        self.import_menu = tk.Menu(self.menu)
        self.import_menu.add_command(label="Import list (txt)", command=self.on_import_txt)
        self.import_menu.add_command(label="Import list (pdf)", command=self.on_import_pdf)
        self.menu.add_cascade(menu=self.import_menu, label="Import")  # put import menu in root
        self.export_menu = tk.Menu(self.menu)
        self.export_menu.add_command(label="Export list (txt)", command=self.export_text)
        self.menu.add_cascade(menu=self.export_menu, label="Export")
        self.menu.entryconfig(1, state=tk.DISABLED)
        self.root["menu"] = self.menu  # set root menu

        font.nametofont("TkDefaultFont").configure(size=TEXTSIZE)
        font.nametofont("TkTextFont").configure(size=TEXTSIZE)
        font.nametofont("TkFixedFont").configure(size=TEXTSIZE)
        font.nametofont("TkMenuFont").configure(size=MENUSIZE)
        font.nametofont("TkHeadingFont").configure(size=MENUSIZE)
        font.nametofont("TkCaptionFont").configure(size=MENUSIZE)
        font.nametofont("TkSmallCaptionFont").configure(size=MENUSIZE)
        font.nametofont("TkIconFont").configure(size=MENUSIZE)
        font.nametofont("TkTooltipFont").configure(size=MENUSIZE)

        # we configure root to only have one grid square our applincation will add
        # a single panel that contains all the application UI.
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        # Main Panel is our single panel application.
        self._main = MainPanel(self.root, self.set_state)

    def set_state(self, edit=False) -> None:
        "set the state"

        if edit:
            self.menu.entryconfig(1, state=tk.NORMAL)
            self.menu.entryconfig(2, state=tk.DISABLED)
        else:
            self.menu.entryconfig(1, state=tk.DISABLED)
            self.menu.entryconfig(2, state=tk.NORMAL)


    def get_path_file(self):
        "gets the path and filename of the current file to save"
        path = os.getcwd()
        file = self._main.get_filename()

        if x := max(file.rfind('/'), file.rfind('\\')) >= 0:
            path = file[0:x]
            file = file[x+1:]

        return path, file

    def on_save(self):
        "Saves data to the last used filename"
        self._main.do_save()

    def on_save_as(self):
        "Saves data to a file, asks for name"
        path, file = self.get_path_file()
        self._main.set_filename(
            filedialog.asksaveasfilename(
                initialdir=path,
                initialfile=file,
                defaultextension=".dat"
            )
        )
        self._main.do_save()

    def on_save_quit(self):
        "Save and Quit"
        if self._u_sure():
            self._main.do_save()  # Save & Quit
            self.root.destroy()  # Quit

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
            self._main.do_save()  # Save & Quit

        self.root.destroy()  # No / Just Quit

    def _u_sure(self):
        """ Check if the User is sure. "are you sure" """
        return bool(
            messagebox.askyesnocancel(
                message="Are you sure?",
                title="Are you sure?"
            )
        )

    def on_reset(self):
        "resets to hardcoded values"
        if self._u_sure():
            self._main.do_reset()

    def on_new(self):
        "clears all data creating a new clean setup"
        if self._u_sure():
            self._main.do_clear()

    def on_load(self):
        "loads data from a file"
        if not self._u_sure():
            return

        path, file = self.get_path_file()
        self._main.set_filename(
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

    def on_import_pdf(self):
        "import from pdf"
        self._main.do_import_pdf(filedialog.askopenfilename(defaultextension=".pdf"))

    def on_import_txt(self):
        "import from txt"
        self._main.do_import_txt(filedialog.askopenfilename())

    def export_text(self):
        "export to text"
        self._main.do_export_text(filedialog.askdirectory())
