"the main panel: holds all the panels; main frame in root window"

import re
from tkinter import E, N, S, W, messagebox, ttk

import dill as pickle

import gendata as dat
from enums import COLWEIGHT, HEIGHT, WIDTH, State, table
from page import PagePanel
from PanelCom import PanelCom
from results import ResultsPanel
from what import WhatPanel
from import_txt import import_txt

FNAME = "tables.dat"


class MainPanel(ttk.Frame, PanelCom):  # pylint: disable=too-many-ancestors,too-many-instance-attributes,too-many-public-methods
    """
    Main frame for the UI

    creates the 3 panels of the application
        what
        page
        result

    handles the glue between the panels, they all call _parent.set_*() to send messages
    to the other panels. The main panel then routes the message to the correct panel.

    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=5, width=WIDTH, height=HEIGHT, **kwargs)
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.root = parent

        # all the panels of our application
        self._what = WhatPanel(self)  # A book, set, list, etc. A collection of rollables
        self._what.grid(column=0, row=0, sticky=(N, S, E, W))

        self._page = PagePanel(self)  # A page is a list of rollables, in a collection
        self._page.grid(column=1, row=0, sticky=(N, S, E, W))

        self._result = ResultsPanel(self)  # this is the resulst of rolling the rollabable
        self._result.grid(column=2, row=0, sticky=(N, S, E, W))

        # our panel are arranged horizontally, in a single row.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=COLWEIGHT[0]) # weights describe relative movement so bigger
        self.columnconfigure(1, weight=COLWEIGHT[1]) # movement is shrinking and growing faster
        self.columnconfigure(2, weight=COLWEIGHT[2]) # smaller numbers stay larger at smaller sizes

        # we start without a selection set.
        self._result.ungrid_set()

        self.numcut = re.compile(r"^[\d\.\,\;\:]+")  # ^ to garantee we only match at the start of the string.

        # initial state
        self.state = State.ROLL
        self._fname = FNAME
        self.do_try_load()

    ###########################################################################
    # main panel state sub panel interop

    def set_state(self, state: State):
        "sets the internal state value to a state"
        self.state = state
        # signal our parts that the state has changed.
        for panel in [self._what, self._page, self._result]:
            panel.set_state()

    def set_page(self, name: str, page: list[table]):
        "set page panel contents"
        self._page.set_page(name, page)

    def set_result_item(self, form: tuple[str, dat.Formula] | tuple[str, table] = ("", [])):
        "set the table for the result page to use"
        self._result.set_item(form)

    def set_filename(self, fname: str):
        "sets the data filename"
        self._fname = fname if fname else FNAME

    def get_filename(self):
        "get the current file name"
        return self._fname

    def get_tk_root(self):
        "get the tk root"
        return self.root

    def insert_new_table(self, title: str, lst: list[str]) -> bool:
        "insert a new table into the all tables list"
        if not self.name_available(title):
            messagebox.showerror(
                message=f"Table name '{title}' already exists,\n please rename the file and try again.",
                title="Table name already exists"
            )  # consider merging the tables.
            return False

        return self._what.add_to_cur((title, lst))



    ###########################################################################
    # "all tables"  table searches

    def get_name_index(self, name: str) -> tuple[int, table] | tuple[None,  None]:
        "returns the index of a table"
        what, _ = self._what.get_what()
        tables = what[0]

        if any((res := x)[0] == name for x in tables):
            return tables.index(res), res[1]

        return None, None

    def has_name(self, name) -> bool:
        "returns true if the name exists"
        what, _ = self._what.get_what()
        tables = what[0]

        return any(x[0] == name for x in tables)

    def name_available(self, name: str) -> bool:
        "returns true if a name is available"
        return not self.has_name(name)

    def get_table(self, idx: int) -> tuple[str, table] | None:
        "returns a table by index"
        what, _ = self._what.get_what()
        tables = what[0]

        if idx >= len(tables) or idx < 0:
            return None

        return tables[idx]

    def get_table_index(self, tab: table) -> tuple[int | None, str]:
        "returns the index of a table"
        what, _ = self._what.get_what()
        tables = what[0]

        # any will stop enumeration when the first comparison is true, and
        # our walrus capture will work as expected.
        if any((res := x)[1] == tab for x in tables):
            return tables.index(res), res[0]

        # return something so we can see in the app what is missing instead of blanks
        return None, "<MISSING>"

    def add_to_all(self, tab: tuple[str, table]) -> bool:
        "adds to the all category"
        if not self.has_name(tab[0]):
            self._what.add_to_all(tab)
            return True
        return False

    def get_name(self, item: dat.MetaFormula | dat.Formula | list | tuple | str) -> str:
        "get name of object, tabels encoded as {tableName}"
        return self._result.get_name(item)  # n.b. this could possibly be moved somewhere else, it was done there first.

    ###########################################################################
    # functions that effect all tables (including "all tables")

    def rename(self, name: str, newname: str) -> bool:
        "renames a table"
        return self._what.rename(name, newname)

    def do_clipboard(self, out: str):
        "copy the results to the clipboard"
        self.root.clipboard_clear()  # clear the clipboard because we are setting its contents
        self.root.clipboard_append(out)

    def check_delete_from_all(self, name):
        "returns trues if deleted from all"
        return self.delete_from_all(name)

    def delete_from_all(self, name):
        "delete a table from the 'all tables' table as well as every other tables"
        if bool( # bool may not be needed could use == True, which is basically the same
            messagebox.askyesnocancel(
                message="Are you sure you want to DELETE from all?",
                title="Are you sure?"
            )
        ):
            self._what.delete_from_all(name)
            return True

        return False

    ###########################################################################
    # menu and internal operations

    def do_save(self):
        "saves the data to disk"
        try:
            with open(self._fname, "wb") as f:
                d = self._what.get_what()
                data = {
                    "what_list": d[0],
                    "what_choices": d[1]
                }
                pickle.dump(data, f)
        except FileNotFoundError:
            pass

    def do_try_load(self):
        "try to load data from the disk"
        try:
            with open(self._fname, "rb", ) as f:
                data = pickle.load(f)
                self._what.set_what_data(data["what_list"], data["what_choices"])
        except FileNotFoundError:
            self.do_reset()
            return

        self._clear_panels()

    def do_reset(self):
        "perform a reset of the data to the hardcoded values"
        self._what.set_what_data(
            [dat.All_tables, dat.Maze_Rats_pages, dat.formulas],
            ["All tables", "Maze Rats pages", "Formulas"],
        )

        self._clear_panels()

    def do_import(self, file: str):
        "Import and merge lists"
        wlist, wchoices = self._what.get_what()

        data = None
        try:
            with open(file, "rb", ) as f:
                data = pickle.load(f)
        except FileNotFoundError:
            return

        append = []  # values to add after combining choices with the same name

        # merge existing lists and track new choices to append.
        for fob, choice in zip(data["what_list"], data["what_choices"]):
            try:
                # if the choice exists merge the lists
                wlist[wchoices.index(choice)] += fob
            except ValueError:
                # if the choice is new add it after this loop.
                append.append((choice, fob))

        # add new choices
        for choice, fob in append:
            wlist.append(fob)
            wchoices.append(choice)

        # set the choices.
        self._what.set_what_data(wlist, wchoices)

    def do_clear(self):
        "Clear all data"

        # we always need an all tables entry.
        self._what.set_what_data(
            [[]],
            ["All tables"],
        )

        self._clear_panels()

    def do_import_pdf(self, filename: str):
        "import from pdf"
        # TODO::
        # dlg = import_pdf(self.root, filename, self)

        # self.wait_window(dlg)
    def do_import_txt(self, filename: str):
        "import from txt file"
        dlg = import_txt(self.root, filename, self)

        self.wait_window(dlg)

    ###########################################################################
    # helpers

    def _filter_list(self, lst: list[str]) -> list[str]:
        "filters a table to remove empty lines and leading numbers"
        lst = [self.numcut.split(x)[1].strip() for x in lst]
        lst = [x for x in lst if x]  # remove empty strings
        return lst

    def _get_title_path_ext_from_file(self, fname: str):
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

    def _clear_panels(self):
        "clear other panels"
        self._page.set_page("", [])
        self.set_result_item()
