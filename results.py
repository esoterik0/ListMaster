"the results panel: displays the results"

import re
import tkinter as tk
from enum import Enum
from tkinter import E, N, S, W, filedialog, ttk

import gendata as dat
from enums import SINGLE, State, table
from ListPanel import ListPanel
from PanelCom import PanelCom

LOG = "rolls.log"


class Widgets(Enum):
    "enums to define which widgets to grid and ungrid at any point in time"
    ROLL = "ROLL"
    FORM = "FORM"


# utility candidate
def int_nun(s: str) -> int | None:
    "returns the string representation of the int or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


class ResultsPanel(ListPanel):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    """
    generates the result panel frame
    displays results
    buttons:
        log results
        reroll results
        generate xls
        copy to clip board
    editing
        test
    """

    def __init__(self, parent: PanelCom, **kwargs):  # pylint: disable=too-many-statements
        # initialize ...
        super().__init__(parent, 2, True, **kwargs)  #  .. our super class
        self._parent: PanelCom = parent

        # state variables
        self.num = SINGLE
        self.path = ""
        self.item = None
        self.item_name = ""
        self.logfile = LOG
        self.sep_pat = re.compile(r"({[\w,|&:+()\[\] ]+)}")
        self.label_pat = re.compile(r"(?P<label>[\w,|&:+()\[\] ]+);{(?P<table>[\w,|&:+()\[\] ]+)}")
        self.semi = re.compile(r";")
        self.backtick = re.compile(r"`")

        # add double click.
        self.lbox.bind("<Double-1>", self.do_double_select)

        # Create and grid our child members; some members will also be grid_removed()ed

        # holds the roll buttons, it can be swaped with a different frame
        self.roll_button_frame = ttk.Frame(self)
        self.roll_button_frame.grid(column=0, row=2, sticky=(E, W))
        self.roll_button_frame.grid_remove()

        # buttons for roll mode
        self.roll_buttons = {}
        self.roll_buttons["reroll"] = ttk.Button(self.roll_button_frame, text="Re-Roll", command=self.do_reroll)
        self.roll_buttons["reroll"].grid(column=0, row=0, sticky=(N, S, E, W))
        self.roll_buttons["num_pages_label"] = ttk.Label(self.roll_button_frame, text="No. Pages")
        self.roll_buttons["num_pages_label"].grid(column=0, row=1, sticky=(N, S, E, W))
        self.num_pages_var = tk.StringVar()
        self.num_pages_var.set(f"{SINGLE}")
        self.roll_buttons["num_pages"] = tk.Entry(self.roll_button_frame, textvariable=self.num_pages_var)
        self.roll_buttons["num_pages"].grid(column=1, row=1, sticky=(N, S, E, W))
        self.roll_buttons["clip_copy"] = ttk.Button(self.roll_button_frame, text="Copy to clipboard", command=self._copy_clip)
        self.roll_buttons["clip_copy"].grid(column=1, row=0, sticky=(N, S, E, W))
        self.roll_buttons["gen_xls"] = ttk.Button(self.roll_button_frame, text="Generate .xls file", command=self.do_xls)
        self.roll_buttons["gen_xls"].grid(column=2, row=1, sticky=(N, S, E, W))
        self.roll_buttons["get_path"] = ttk.Button(self.roll_button_frame, text="Choose path", command=self.do_path)
        self.roll_buttons["get_path"].grid(column=2, row=0, sticky=(N, S, E, W))
        self.roll_buttons["set_log"] = ttk.Button(self.roll_button_frame, text="Set log file", command=self.do_set_log)
        self.roll_buttons["set_log"].grid(column=0, row=2, sticky=(N, S, E, W))
        self.roll_buttons["log_roll"] = ttk.Button(self.roll_button_frame, text="Reroll & log", command=self.do_logroll)
        self.roll_buttons["log_roll"].grid(column=1, row=2, sticky=(N, S, E, W))
        self.roll_buttons["log"] = ttk.Button(self.roll_button_frame, text="Log the roll", command=self.do_log)
        self.roll_buttons["log"].grid(column=2, row=2, sticky=(N, S, E, W))

        # holds the edit buttons; swapped in during edit mode.
        self.edit_button_frame = ttk.Frame(self)
        self.edit_button_frame.grid(column=0, row=1, sticky=(E, W))
        self.edit_button_frame.grid_remove()

        # buttons for edit mode
        self.edit_buttons = {}
        self.edit_buttons["add_item"] = ttk.Button(self.edit_button_frame, text="Add Item", command=self.do_add)
        self.edit_buttons["add_item"].grid(column=0, row=0, sticky=(N, S, E, W))
        self.edit_buttons["edit_item"] = ttk.Button(self.edit_button_frame, text="Edit Item", command=self.do_edit)
        self.edit_buttons["edit_item"].grid(column=0, row=1, sticky=(N, S, E, W))
        self.edit_buttons["done"] = ttk.Button(self.edit_button_frame, text="Done Editing", command=self.do_done)
        self.edit_buttons["done"].grid(column=1, row=1, sticky=(N, S, E, W))

        # configure the grids
        # self.rowconfigure(1, weight=1)
        # 3x3 grid
        for i in range(3):
            self.roll_button_frame.rowconfigure(i, weight=1)
            self.roll_button_frame.columnconfigure(i, weight=1)
        # 2x2 grid
        for i in range(2):
            self.edit_button_frame.columnconfigure(i, weight=1)
            self.edit_button_frame.rowconfigure(i, weight=1)

    def get_effective_len(self, item):
        "metaformulas are actually one space bigger."
        match(item):
            case list() | dat.Formula():
                return len(item)
            case dat.MetaFormula():
                return len(item)+1

    def accept_edit(self, newtext: str):
        "validate last selection, delete"
        if self.last_selection is None:
            return

        if self.last_selection >= self.get_effective_len(self.item):
            return

        if len(newtext) == 0:
            match(self.item):
                case dat.Formula() | dat.MetaFormula():
                    del self.item.formula[self.last_selection]
                    del self.item.labels[self.last_selection]
                case list():
                    del self.item[self.last_selection]

        # if we need to reuse this move it at that point.
        def _convert(text: str):
            if self._is_safe(text):
                return text
            # the above if will take care of strings that don't have {} in them
            if text.count("{") == text.count("}"): # check that we have pairs of {}
                out = [x for x in self.sep_pat.split(text) if x] # filter empty strings; sep_pat filters out '}'
                #assert len(out) > 0
                if len(out) == 1:
                    #assert out[0][0] == "{"
                    if self._is_safe(tab := out[0][1:]):
                        return self._parent.get_name_index(tab)[1]
                else:
                    put = []
                    for item in out:
                        if item[0]=="{":
                            if self._is_safe(tab := item[1:]):
                                put.append(self._parent.get_name_index(tab)[1])
                        elif self._is_safe(item):
                            put.append(item)

                    return tuple(put)
            return ""

        # if we need to reuse this move it at that point.
        def convert(text: str):
            if text.count('`') > 0:
                out = []
                for txt in self.backtick.split(text):
                    out.append(_convert(txt))
                return out
            return _convert(text)

        newtext = convert(newtext)

        if not newtext:
            return

        match (self.item):
            case dat.Formula():
                if newtext.count(';') != 1:
                    return
                label, text = self.semi.split(newtext)
                if self._is_safe(label):
                    if txt := convert(text):
                        self.item.formula[self.last_selection] = txt
                        self.item.label[self.last_selection] = label
            case dat.MetaFormula():
                if self.last_selection == 0:
                    self.item.labels = list(s.strip() for s in self.semi.split(newtext))
                else:
                    if txt := convert(newtext):
                        self.item.formula[self.last_selection-1] = txt
            case list():
                if txt := convert(newtext):
                    self.item[self.last_selection] = txt

        self.set_result()

    def drag(self, start, end):
        "do the drag"

        if self._parent.state != State.EDIT:
            return

        if isinstance(self.item, dat.MetaFormula):
            if (start == 0 or end == 0):
                return

        # swap them
        super().drag(start, end)

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
                self.set_result([])
                self.ungrid_set()

    def set_item_edit(self):
        "sets the item to edit"
        if self.item:
            self.choices = []
            match self.item:
                case dat.MetaFormula():
                    self.choices = [";".join(self.item.labels)] + ["`".join(
                        self.get_name(itm) for itm in item.formula
                        ) for item in self.item.formula
                    ]
                case dat.Formula():
                    self.choices = [
                        f"{label};{self.get_name(item)}"
                        for item, label in zip(self.item.formula, self.item.labels)
                    ]
                case list():
                    self.choices = [self.get_name(item) for item in self.item]
            self.set_result()

    def set_item_roll(self):
        "sets the formula or table to roll on and rolls it."
        self.ungrid_set()
        self.grid_set()
        self.do_reroll()

    def set_state(self):
        "set state handler called when _parent changes state"
        # clear panel
        # self.item_name, self.item = "", None
        # self.set_result([])

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
        self.grid_set()

        self.set_item((self.item_name, self.item))

    def set_result(self, lst: list | None = None):
        "sets the results list, used for setting and clearing the list"
        # use results_list as is if called without a parameter
        if lst is not None:  # empty lists are allowed
            self.choices = lst
        self._update_lbox()

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
                        self.choices = [self.item_name] + [dat.gen_list(self.item) for _ in range(self.num)]
                    case dat.MetaFormula() | dat.Formula():
                        self.choices = [f"{type(self.item).__name__}: {self.item_name}"] + [
                            b + ": " + o  # label: object format for formulas
                            for b, o in zip(
                                self.item.labels,
                                dat.gen_form(self.item)
                            )
                        ]
                    case _:
                        pass
            else:
                self.choices = []  # clear the list
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

    def do_lbox_sel(self, *args):  # pylint: disable=unused-argument
        "selection clicking"
        self._sel()

    def do_double_select(self, *args):  # pylint: disable=unused-argument
        "selection double clicking"
        self._sel()
        if self._parent.state == State.EDIT:
            return self.do_edit()

        return "return"

    def do_edit(self):
        "popup an edit window in place"
        if self.last_selection is not None:
            self._start_edit(self.choices[self.last_selection])

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
            print(f"rolling {self.item_name}", *self.choices, sep='\n', end='\n\n', file=f)

    def _copy_clip(self):
        "copy the results to the clipboard"
        self._parent.do_clipboard("\n".join(self.choices))

    def _update_num(self):
        "updates self.num"
        num = int_nun(self.num_pages_var.get())  # try to get the number
        self.num = num if num else SINGLE  # if we don't have a number num is None

    def get_name(self, item: dat.MetaFormula | dat.Formula | list | tuple | str) -> str:
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
            they should probably be separated by a space " " or something.

            ex. "pre{table1} {table2}mid{table3} post"

        strings are passed unchanged
        """
        match item:
            case dat.MetaFormula() | dat.Formula() | list():
                _, name = self._parent.get_table_index(item)
                return f"{{{name}}}"
            case tuple():
                return f"{"".join(self.get_name(itm) for itm in item)}"
            case str():
                return item

