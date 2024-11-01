"listmaster: roll on random tables"
import tkinter as tk
from tkinter import E, N, S, W, ttk

import gendata as dat


def ridgeFrame(content, **kwargs):
    "returns a tk.ttk.frame with ridge relief & kwargs"
    return ttk.Frame(content, borderwidth=5, relief="ridge", **kwargs)


def intnun(s: str) -> int | None:
    "returns the int represented by the string or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


WIDTH = 75
HEIGHT = 25
SINGLE = 5


class ListMaster:
    "class handling the UI for the ListMaster program"
    def __init__(self):
        self.root = tk.Tk()
        self.main = ttk.Frame(self.root, padding=5, width=WIDTH, height=HEIGHT)
        self.main.grid(column=0, row=0, sticky=(N, S, E, W))

        self.whatframe = ridgeFrame(self.main)
        self.whatframe.grid(column=0, row=0, sticky=(N, S, E, W))

        self.whatlist = [dat.All_tables, dat.Maze_Rats_pages, dat.formulas]
        whatchoices = ["All tables", "Maze Rats pages", "Formulas"]
        whatchoicevar = tk.StringVar(value=whatchoices)

        self.what = tk.Listbox(self.whatframe, listvariable=whatchoicevar, width=int(WIDTH/5), height=HEIGHT)
        self.what.grid(column=0, row=0, sticky=(N, S, E, W))
        self.what.bind("<<ListboxSelect>>", self.dowhat)

        self.pageframe = ridgeFrame(self.main)
        self.pageframe.grid(column=1, row=0, sticky=(N, S, E, W))

        self.pagechoices = tk.StringVar()

        self.page = tk.Listbox(self.pageframe, listvariable=self.pagechoices, width=int(3*WIDTH/5), height=HEIGHT)
        self.page.grid(column=0, row=0, sticky=(N, S, E, W))
        self.page.bind("<<ListboxSelect>>", self.dopage)

        self.resultframe = ridgeFrame(self.main)
        self.resultframe.grid(column=2, row=0, sticky=(N, S, E, W))

        self.results = tk.StringVar()

        self.result = tk.Listbox(self.resultframe, listvariable=self.results, width=int(4*WIDTH/5), height=HEIGHT)
        self.result.grid(column=0, row=0, sticky=(N, S, E, W))

        self.buttonframe = ttk.Frame(self.resultframe)
        self.buttonframe.grid(column=0, row=1, sticky=(E, W))

        self.reroll = ttk.Button(self.buttonframe, text="Re-Roll", command=self.doreroll)
        self.reroll.grid(column=0, row=0)
        self.reroll.grid_remove()

        self.genxls = ttk.Button(self.buttonframe, text="Generate .xls file", command=self.doxls)
        self.genxls.grid(column=1, row=0)

        self.numpageslabel = ttk.Label(self.buttonframe, text="No. Pages")
        self.numpageslabel.grid(column=0, row=1)

        self.numpagesvar = tk.StringVar()
        self.numpagesvar.set("5")

        self.numpages = tk.Entry(self.buttonframe, textvariable=self.numpagesvar, width=10)
        self.numpages.grid(column=1, row=1)

        self.clipcopy = ttk.Button(self.buttonframe, text="Copy to clip board", command=self.copyclip)
        self.clipcopy.grid(column=2, row=0)
        self.clipcopy.grid_remove()

        self.ungridform()  # we only want to grid these widgets when we have a formula selected.
        self._configure_rows()  # call the helper to configure cols/rows

        self.form: dat.formula | list = None
        self.formname = ""
        self.curpage = None

        self.result_list = None

        self.root.mainloop()  # we never exit the constructor.

    def copyclip(self):
        "copy the results to the clipboard"
        self.root.clipboard_clear()  # clear the clipboard because we are setting its contents
        # this is safe because the button that calls this method will not be shown unless results has contents
        self.root.clipboard_append("\n".join(self.result_list))

    def _configure_rows(self):
        "helper: configures rows and columns; it takes so many calls."
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=2)
        self.main.columnconfigure(2, weight=4)
        self.whatframe.rowconfigure(0, weight=1)
        self.whatframe.columnconfigure(0, weight=1)
        self.pageframe.rowconfigure(0, weight=1)
        self.pageframe.columnconfigure(0, weight=1)
        self.resultframe.rowconfigure(0, weight=1)
        self.resultframe.columnconfigure(0, weight=1)
        self.buttonframe.rowconfigure(0, weight=1)
        self.buttonframe.rowconfigure(1, weight=1)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)
        self.buttonframe.columnconfigure(2, weight=1)

    def gridform(self):
        "helper: grids all formula (.xlsx) related widgets"
        self.genxls.grid()
        self.numpages.grid()
        self.numpageslabel.grid()

    def ungridform(self):
        "helper: ungrids (grid_remove()) all formula (.xlsx) related widgets"
        self.genxls.grid_remove()
        self.numpages.grid_remove()
        self.numpageslabel.grid_remove()

    def gridroll(self):
        "adds reroll and clipcopy to the buttonframe"
        self.reroll.grid()
        self.clipcopy.grid()

    def ungridroll(self):
        "removes reroll and clipcopy from the button frame"
        self.reroll.grid_remove()
        self.clipcopy.grid_remove()

    def dowhat(self, e):
        "handles the selection on the what column"
        sel = self.what.curselection()

        if (len(sel) == 1):
            self.curpage = self.whatlist[sel[0]]
            self.pagechoices.set([n for n, _ in self.curpage])
            self.results.set([])
            self.ungridroll()
            self.ungridform()

    def dopage(self, e):
        "handles the selections on the page column"
        sel = self.page.curselection()
        if (len(sel) == 1):
            self.formname, self.form = self.curpage[sel[0]]
            self.gridroll()

            if isinstance(self.form, dat.formula):
                self.gridform()
            else:
                self.ungridform()

            self.doreroll()

    def doreroll(self):
        "rerolls the results column"
        if (self.form is not None):
            match(self.form):
                case list():
                    self.result_list = [self.formname] + [dat.gen_list(self.form) for _ in range(SINGLE)]
                    self.results.set(self.result_list)
                case dat.formula():
                    self.result_list = [
                        b + ": " + o
                        for b, o in zip(
                            self.form.labels,
                            dat.gen_form(self.form)
                        )
                    ]
                    self.results.set(self.result_list)
                case _:
                    self.results.set([])

    def doxls(self):
        "button processor makes .xlsx files"
        num = intnun(self.numpagesvar.get())
        num = num if num else 5
        dat.Manufacture(
            lambda: dat.general_generator(self.form),
            self.formname,
            num,
            self.form.split
        )


if __name__ == "__main__":
    ListMaster()
