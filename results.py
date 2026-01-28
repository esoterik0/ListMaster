"the results panel: displays the results"

import tkinter as tk
from enum import Enum
from tkinter import E, N, S, W, filedialog, ttk

import gendata as dat
from edinsitu import start_edit
from enums import HEIGHT, SINGLE, WIDTH, State

#type alias
table = list[str | list | tuple]  # pylint: disable=invalid-name

LOG = "rolls.log"


class Widgets(Enum):
    "enums to define which widgets to grid and ungrid at various points"
    ROLL = "ROLL"
    FORM = "FORM"


# utility candidate
def int_nun(s: str) -> int | None:
    "returns the string representation of the int or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


class ResultsPanel(ttk.Frame):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    """
    generates the result panel frame
    displays results
    buttons:
        log results
        reroll results
        generate xls
        copy to clip board
    editing
        todo
    """

    def __init__(self, parent, **kwargs):  # pylint: disable=too-many-statements
        self._parent = parent
        # state variables
        self.num = SINGLE
        self.path = ""
        self.item = None
        self.item_name = ""
        self.last_selection = None
        self.logfile = LOG

        # initialize ...
        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)  #  .. our super class
        self.grid(column=2, row=0, sticky=(N, S, E, W))  # ... oursevles   # type: ignore # this is the way tk works

        # Create and grid our child members; some members will also be grid_removed()ed

        # Results
        self.result_list = []  # our list; self.results.set(self.result_list)
        self.results = tk.StringVar()  # tk list
        self.result = tk.Listbox(self, listvariable=self.results, width=int(4*WIDTH/5), height=HEIGHT)
        self.result.grid(column=0, row=0, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.result.bind("<<ListboxSelect>>", self.do_select)
        self.result.bind("<Double-1>", self.do_double_select)

        # holds the roll buttons, it can be swaped with a different frame
        self.roll_button_frame = ttk.Frame(self)
        self.roll_button_frame.grid(column=0, row=1, sticky=(E, W)) # type: ignore # this is the way tk works
        self.roll_button_frame.grid_remove()

        # buttons for roll mode
        self.roll_buttons = {}
        self.roll_buttons["reroll"] = ttk.Button(self.roll_button_frame, text="Re-Roll", command=self.do_reroll)
        self.roll_buttons["reroll"].grid(column=0, row=0, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["num_pages_label"] = ttk.Label(self.roll_button_frame, text="No. Pages")
        self.roll_buttons["num_pages_label"].grid(column=0, row=1, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.num_pages_var = tk.StringVar()
        self.num_pages_var.set(f"{SINGLE}")
        self.roll_buttons["num_pages"] = tk.Entry(self.roll_button_frame, textvariable=self.num_pages_var)
        self.roll_buttons["num_pages"].grid(column=1, row=1, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["clip_copy"] = ttk.Button(
            self.roll_button_frame,
            text="Copy to clipboard",
            command=self._copy_clip
        )
        self.roll_buttons["clip_copy"].grid(column=1, row=0, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["gen_xls"] = ttk.Button(self.roll_button_frame, text="Generate .xls file", command=self.do_xls)
        self.roll_buttons["gen_xls"].grid(column=2, row=1, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["get_path"] = ttk.Button(self.roll_button_frame, text="Choose path", command=self.do_path)
        self.roll_buttons["get_path"].grid(column=2, row=0, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["set_log"] = ttk.Button(self.roll_button_frame, text="Set log file", command=self.do_set_log)
        self.roll_buttons["set_log"].grid(column=0, row=2, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["log_roll"] = ttk.Button(self.roll_button_frame, text="Reroll & log", command=self.do_logroll)
        self.roll_buttons["log_roll"].grid(column=1, row=2, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.roll_buttons["log"] = ttk.Button(self.roll_button_frame, text="Log the roll", command=self.do_log)
        self.roll_buttons["log"].grid(column=2, row=2, sticky=(N, S, E, W)) # type: ignore # this is the way tk works

        # holds the edit buttons; swapped in during edit mode.
        self.edit_button_frame = ttk.Frame(self)
        self.edit_button_frame.grid(column=0, row=1, sticky=(E, W)) # type: ignore # this is the way tk works
        self.edit_button_frame.grid_remove()

        # buttons for edit mode
        self.edit_buttons = {}
        self.edit_buttons["add_item"] = ttk.Button(self.edit_button_frame, text="Add Item", command=self.do_add)
        self.edit_buttons["add_item"].grid(column=0, row=0, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.edit_buttons["edit_item"] = ttk.Button(self.edit_button_frame, text="Edit Item", command=self.do_edit)
        self.edit_buttons["edit_item"].grid(column=0, row=1, sticky=(N, S, E, W)) # type: ignore # this is the way tk works
        self.edit_buttons["done"] = ttk.Button(self.edit_button_frame, text="Done Editing", command=self.do_done)
        self.edit_buttons["done"].grid(column=1, row=1, sticky=(N, S, E, W)) # type: ignore # this is the way tk works

        # configure the grids
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # 3x3 grid
        for i in range(3):
            self.roll_button_frame.rowconfigure(i, weight=1)
            self.roll_button_frame.columnconfigure(i, weight=1)
        # 2x2 grid
        for i in range(2):
            self.edit_button_frame.columnconfigure(i, weight=1)
            self.edit_button_frame.rowconfigure(i, weight=1)

    def set_item(self, form: tuple[str, dat.Formula] | tuple[str, table]):
        "dispatches based on mode"
        name, item = form
        if name:
            self.item_name, self.item = name, item

            match self._parent.state:
                case State.ROLL:
                    self.set_item_roll()
                case State.EDIT:
                    self.set_item_edit()
                case _:
                    pass

            self.grid_set()
        else:
            if self._parent.state == State.ROLL:
                self.item_name, self.item = "", []
                self.ungrid_set()

    def set_item_edit(self):
        "sets the item to edit"
        if self.item:
            self.result_list = []
            match self.item:
                case dat.MetaFormula():
                    self.result_list = [",".join(
                        self._get_name(itm) for itm in item.formula
                        ) for item in self.item.formula
                    ]  # + ["label: " + b for b in self.item.labels]
                    # todo figure out labels for MetaFormula; and how to make/edit them
                case dat.Formula():
                    self.result_list = [self._get_name(item) for item in self.item.formula]
                case list():
                    self.result_list = [self._get_name(item) for item in self.item]
            self.set_result()

    def set_item_roll(self):
        "sets the formula or table to roll on and rolls it."
        self.ungrid_set()
        self.grid_set()
        self.do_reroll()

    def set_state(self):
        "set state handler called when _parent changes state"
        # clear panel
        self.item_name, self.item = "", None
        self.set_result([])

        match self._parent.state:
            case State.ROLL:
                self.edit_button_frame.grid_remove()
                self.roll_button_frame.grid()
            case State.EDIT:
                self.roll_button_frame.grid_remove()
                self.edit_button_frame.grid()
            case _:
                pass

        self.ungrid_set()

    def set_result(self, lst: list | None = None):
        "sets the results list, used for setting and clearing the list"
        # use results_list as is if called without a parameter
        if lst is not None:  # empty lists are allowed
            self.result_list = lst
        self.results.set(self.result_list)  # type: ignore # this is the way tk works

    def ungrid_set(self):
        "removes widgets from the grid bassed on mode"
        match self._parent.state:
            case State.ROLL:
                self.roll_button_frame.grid_remove()
                # we only un/grid the buttons that change
                self.roll_buttons["gen_xls"].grid_remove()
                self.roll_buttons["get_path"].grid_remove()
            case State.EDIT:
                self.edit_button_frame.grid_remove()
                self.roll_button_frame.grid_remove()
            case _:
                pass

    def grid_set(self):
        "adds widgets bassed on mode"
        match self._parent.state:
            case State.EDIT:
                self.edit_button_frame.grid()
            case State.ROLL:
                self.roll_button_frame.grid()
                # we only un/grid the buttons that change
                match self.item:
                    case dat.MetaFormula() | dat.Formula():
                        self.roll_buttons["gen_xls"].grid()
                        self.roll_buttons["get_path"].grid()
                        self.roll_buttons["num_pages_label"].configure(text="No. Pages")
                    case list():
                        self.roll_buttons["num_pages_label"].configure(text="No. to Roll")
                    case _:
                        pass  # don't do anything if None or unexpected.

    def do_reroll(self):
        "handles the re-roll button, generates and populates the results column"
        if self._parent.state == State.ROLL:
            if self.item:
                match(self.item):
                    case list():
                        self._update_num()
                        self.result_list = [self.item_name] + [dat.gen_list(self.item) for _ in range(self.num)]
                    case dat.MetaFormula() | dat.Formula():
                        self.result_list = [f"{type(self.item).__name__}: {self.item_name}"] + [
                            b + ": " + o  # label: object format for formulas
                            for b, o in zip(
                                self.item.labels,
                                dat.gen_form(self.item)
                            )
                        ]
                    case _:
                        pass
            else:
                self.result_list = []  # clear the list
            self.set_result()

    def do_path(self):
        "gets the path"
        self.path = filedialog.askdirectory()
        if self.path:
            self.path += "/"  # prepare for appending to later

    def do_xls(self):
        "Handles the Generate .xls button, currently makes double sided three hole punched 8 1/2 x 11 pages."
        self._update_num()
        dat.manufacture(self.item, self.path, self.item_name, self.num)

    def do_done(self):
        "handle the done editing button"
        # clear the panel
        self.item, self.item_name = None, ""
        self.set_result([])
        self.ungrid_set()

    def do_add(self):
        "add item to item button"

    def do_select(self, *args):  # pylint: disable=unused-argument
        "selection clicking"
        self._sel()

    def do_double_select(self, *args):  # pylint: disable=unused-argument
        "selection double clicking"
        self._sel()

        if self._parent.state == State.EDIT:
            return self.do_edit()

        return None

    def do_edit(self):
        "popup an edit window in place"
        return start_edit(
            self.result,
            self.last_selection,
            self._check_accept_edit,
            self.result_list[self.last_selection]
        )

    def do_set_log(self):
        "set log file button"
        if log := filedialog.asksaveasfilename():
            self.logfile = log

    def do_logroll(self):
        "reroll and log the results button"
        self.do_reroll()
        self.do_log()

    def do_log(self):
        "log the results button"
        with open(self.logfile, "a", encoding="utf-8") as f:
            print(f"rolling {self.item_name}", *self.result_list, sep='\n', end='\n\n', file=f)

    def _copy_clip(self):
        "copy the results to the clipboard"
        self._parent.clipboard("\n".join(self.result_list))

    def _update_num(self):
        "updates self.num"
        num = int_nun(self.num_pages_var.get())  # try to get the number
        self.num = num if num else SINGLE  # if we don't have a number num is None

    def _get_name(self, item: dat.MetaFormula | dat.Formula | list | tuple | str) -> str:
        """
        get a translated name from an item

        for dat.MetaFormula, dat.Formula, list
            the name is looked up via parent
            and returned in braces {}

        for tuples
            the name of each item in in the tuple is looked up by calling this function recursively
            in the form of (name1name2...namen)
            strings can be concatenated together, so each tuple can not have more than one string in
            a row, a table must be between any strings in the tuple, one can have multiple tables, but
            they should probably be separated by a space " ".

            ex. "pre {table1} {table2} mid{table3} post"

        strings are passed unchanged
        """
        match item:
            case dat.MetaFormula() | dat.Formula() | list():
                _, name = self._parent.item_index(item)
                return f"{{{name}}}"
            case tuple():
                return f"({"".join(self._get_name(itm) for itm in item)})"
            case str():
                return item

    def _sel(self):
        "current->last selection logic helper function"
        sel = self.result.curselection()

        if len(sel) == 1:
            self.last_selection = sel[0]

    def _check_accept_edit(self, val: str):
        "check and accept an edit"
