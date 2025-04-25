"the results panel: displays the results"

import tkinter as tk
from tkinter import E, N, S, W, filedialog, ttk

import gendata as dat
from enums import HEIGHT, SINGLE, WIDTH, Widgets, State


def int_nun(s: str) -> int | None:
    "returns the int represented by the string or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


class ResultsPanel(ttk.Frame):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    "generates the page frame, for choosing, inspecting, or editing which 'page', formula or table"
    def __init__(self, parent, **kwargs):
        self._parent = parent
        self.num = SINGLE
        self.path = ""
        self.form = None
        self.form_name = ""

        super().__init__(parent, borderwidth=5, relief="ridge", **kwargs)
        self.grid(column=2, row=0, sticky=(N, S, E, W))

        self.results = tk.StringVar()
        self.result_list = []

        self.result = tk.Listbox(self, listvariable=self.results, width=int(4*WIDTH/5), height=HEIGHT)
        self.result.grid(column=0, row=0, sticky=(N, S, E, W))

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))

        self.reroll = ttk.Button(self.button_frame, text="Re-Roll", command=self.do_reroll)
        self.reroll.grid(column=0, row=0)

        self.num_pages_label = ttk.Label(self.button_frame, text="No. Pages")
        self.num_pages_label.grid(column=0, row=1)

        self.num_pages_var = tk.StringVar()
        self.num_pages_var.set(f"{SINGLE}")

        self.num_pages = tk.Entry(self.button_frame, textvariable=self.num_pages_var)
        self.num_pages.grid(column=1, row=1)

        self.clip_copy = ttk.Button(self.button_frame, text="Copy to clip board", command=self._copy_clip)
        self.clip_copy.grid(column=1, row=0)

        self.gen_xls = ttk.Button(self.button_frame, text="Generate .xls file", command=self.do_xls)
        self.gen_xls.grid(column=2, row=1)

        self.get_path = ttk.Button(self.button_frame, text="Choose path", command=self.do_path)
        self.get_path.grid(column=2, row=0)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

    def set_formula(self, form):
        "sets the formula or table to roll on"
        self.form_name, self.form = form

    def do_reroll(self):
        "handles the re-roll button, generates and populates the results column"
        if self.form is not None:
            match(self.form):
                case list():
                    self._update_num()
                    self.result_list = [self.form_name] + [dat.gen_list(self.form) for _ in range(self.num)]
                case dat.Formula():
                    self.result_list = [
                        b + ": " + o
                        for b, o in zip(
                            self.form.labels,
                            dat.gen_form(self.form)
                        )
                    ]
        else:
            self.result_list = []
        self.set_result(self.result_list)

    def set_result(self, lst: list):
        "sets the results string, used for clearing the list"
        self.results.set(lst)

    def do_path(self):
        "gets the path"
        self.path = filedialog.askdirectory()
        if self.path:
            self.path += "/"

    def _update_num(self):
        "updates self.num"
        num = int_nun(self.num_pages_var.get())  # try to get the number
        self.num = num if num else SINGLE  # if we don't have a number num is None

    def do_xls(self):
        "Handles the Generate .xls button, currently makes double sided three hole punched 8 1/2 x 11 pages."
        self._update_num()
        dat.manufacture(self.form, self.path, self.form_name, self.num)

    def _copy_clip(self):
        "copy the results to the clipboard"
        self._parent.clipboard("\n".join(self.result_list))

    def ungrid_set(self):
        "removes widgets from the grid"
        self.button_frame.grid_remove()
        self.reroll.grid_remove()
        self.gen_xls.grid_remove()
        self.get_path.grid_remove()
        self.num_pages_label.configure(text="")

    def grid_set(self, widget: Widgets):
        "adds widgets to the grid"

        match widget:
            case Widgets.ROLL:
                self.button_frame.grid()
                self.reroll.grid()
                self.num_pages_label.configure(text="No. to Roll")
            case Widgets.FORM:
                self.button_frame.grid()
                self.gen_xls.grid()
                self.get_path.grid()
                self.num_pages_label.configure(text="No. Pages")
