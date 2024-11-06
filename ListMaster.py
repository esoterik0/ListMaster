"ListMaster.py program to dice random lists"
import tkinter as tk
from tkinter import E, N, S, W, ttk

import gendata as dat


def ridge_frame(content, **kwargs):
    "returns a window with borderwidth=5 and relief='ridge' plus any kwargs"
    return ttk.Frame(content, borderwidth=5, relief="ridge", **kwargs)


def int_nun(s: str) -> int | None:
    "returns the int represented by the string or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


WIDTH = 75
HEIGHT = 25


class ListMaster:  # pylint: disable=too-many-instance-attributes
    """
    Tkinter UI for generating random choices, and creating tables and formulas.
    """
    def __init__(self, autostart=True):
        "Initializes the the UI; utilizes many helper functions"
        self.root = tk.Tk()
        self.form: dat.Formula | list = None
        self.form_name = ""
        self.path = ""
        self.cur_page = None

        self.gen_main()
        self.gen_what()
        self.gen_page()
        self.gen_results()
        self.gen_buttons()
        self.gen_form_buttons()
        self.config_grid()

        if autostart:
            self.start()

    def start(self):
        "Runs the tk main loop"
        self.root.mainloop()

    def gen_main(self):
        "Generates the main frame that all widgets will be part of"
        self.main = ttk.Frame(self.root, padding=5, width=WIDTH, height=HEIGHT)
        self.main.grid(column=0, row=0, sticky=(N, S, E, W))

    def gen_what(self):
        "Generates the what frame, for choosing what category"
        self.what_frame = ridge_frame(self.main)
        self.what_frame.grid(column=0, row=0, sticky=(N, S, E, W))

        self.what_list = [dat.All_tables, dat.Maze_Rats_pages, dat.formulas]
        what_choices = ["All tables", "Maze Rats pages", "Formulas"]
        what_choice_var = tk.StringVar(value=what_choices)

        self.what = tk.Listbox(self.what_frame, listvariable=what_choice_var, width=int(WIDTH/5), height=HEIGHT)
        self.what.grid(column=0, row=0, sticky=(N, S, E, W))
        self.what.bind("<<ListboxSelect>>", self.do_what)

    def gen_page(self):
        "generates the page frame, for choosing, inspecting, or editing which 'page', formula or table"
        self.page_frame = ridge_frame(self.main)
        self.page_frame.grid(column=1, row=0, sticky=(N, S, E, W))

        self.page_choices = tk.StringVar()

        self.page = tk.Listbox(self.page_frame, listvariable=self.page_choices, width=int(3*WIDTH/5), height=HEIGHT)
        self.page.grid(column=0, row=0, sticky=(N, S, E, W))
        self.page.bind("<<ListboxSelect>>", self.do_page)

    def gen_results(self):
        "generates the result frame, for viewing the results, inspecting or editing formulas or tables."
        self.result_frame = ridge_frame(self.main)
        self.result_frame.grid(column=2, row=0, sticky=(N, S, E, W))

        self.results = tk.StringVar()

        self.result = tk.Listbox(self.result_frame, listvariable=self.results, width=int(4*WIDTH/5), height=HEIGHT)
        self.result.grid(column=0, row=0, sticky=(N, S, E, W))

    def gen_buttons(self):
        "generate button frame and some buttons; must be called before other gen_*_buttons. "
        self.button_frame = ttk.Frame(self.result_frame)
        self.button_frame.grid(column=0, row=1, sticky=(E, W))

        self.reroll = ttk.Button(self.button_frame, text="Re-Roll", command=self.do_reroll)
        self.reroll.grid(column=0, row=0)
        self.reroll.grid_remove()

    def gen_form_buttons(self):
        "generates the extra buttons for dealing with formulas"
        self.gen_xls = ttk.Button(self.button_frame, text="Generate .xls file", command=self.do_xls)
        self.gen_xls.grid(column=1, row=0)

        self.num_pages_label = ttk.Label(self.button_frame, text="No. Pages")
        self.num_pages_label.grid(column=0, row=1)

        self.num_pages_var = tk.StringVar()
        self.num_pages_var.set("5")

        self.num_pages = tk.Entry(self.button_frame, textvariable=self.num_pages_var)
        self.num_pages.grid(column=1, row=1)

        self.ungrid_form()

    def config_grid(self):
        "calls column/rowconfigure on all our frames to set weights for resizing"
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=2)
        self.main.columnconfigure(2, weight=4)
        self.what_frame.rowconfigure(0, weight=1)
        self.what_frame.columnconfigure(0, weight=1)
        self.page_frame.rowconfigure(0, weight=1)
        self.page_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)

    def grid_form(self):
        "grids buttons for formulas."
        self.gen_xls.grid()
        self.num_pages.grid()
        self.num_pages_label.grid()

    def ungrid_form(self):
        "ungrids buttons for formulas"
        self.gen_xls.grid_remove()
        self.num_pages.grid_remove()
        self.num_pages_label.grid_remove()

    def do_what(self, e):  # pylint: disable=unused-argument
        "handles the 'what' column, which is the top level category, and fills out the page choices"
        sel = self.what.curselection()

        if len(sel) == 1:
            self.cur_page = self.what_list[sel[0]]
            self.page_choices.set([n for n, _ in self.cur_page])
            self.results.set([])
            self.reroll.grid_remove()
            self.ungrid_form()

    def do_page(self, e):  # pylint: disable=unused-argument
        "handles the 'page' column to choose which table, page, or formula to generate from; triggers re-roll"
        sel = self.page.curselection()
        if (len(sel) == 1):
            self.form_name, self.form = self.cur_page[sel[0]]
            self.reroll.grid()

            if isinstance(self.form, dat.Formula):
                self.grid_form()
            else:
                self.ungrid_form()

            self.do_reroll()

    def do_reroll(self):
        "handles the re-roll button, generates and populates the results column"
        if (self.form is not None):
            out = dat.gen3(self.form)
            match(out):
                case str():
                    self.results.set([f"{self.form_name}: {out}"])
                case list():
                    self.results.set([f"{b}: {o}" for b, o in zip(self.form.labels, out)])
                case _:
                    self.results.set([])

    def do_xls(self):
        "Handles the Generate .xls button, currently makes double sided three hole punched 8 1/2 x 11 pages."
        num = int_nun(self.num_pages_var.get())  # try to get the number
        num = num if num else 5  # if we don't have a number num is None
        dat.manufacture(self.form, self.path, self.form_name, num)


if __name__ == "__main__":
    ListMaster()
