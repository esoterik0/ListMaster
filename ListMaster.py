import tkinter as tk
from tkinter import E, N, S, W, ttk

import gendata as dat


def ridgeFrame(content, **kwargs):
    return ttk.Frame(content, borderwidth=5, relief="ridge", **kwargs)


def intnun(s: str) -> int | None:
    "returns the int represented by the string or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None


width = 75
height = 25


class ListMaster:
    def __init__(self):
        self.root = tk.Tk()
        self.main = ttk.Frame(self.root, padding=5, width=width, height=height)
        self.main.grid(column=0, row=0, sticky=(N, S, E, W))

        self.whatframe = ridgeFrame(self.main)
        self.whatframe.grid(column=0, row=0, sticky=(N, S, E, W))

        self.whatlist = [dat.All_tables, dat.Maze_Rats_pages, dat.formulas]
        whatchoices = ["All tables", "Maze Rats pages", "Formulas"]
        whatchoicevar = tk.StringVar(value=whatchoices)

        self.what = tk.Listbox(self.whatframe, listvariable=whatchoicevar, width=int(width/5), height=height)
        self.what.grid(column=0, row=0, sticky=(N, S, E, W))
        self.what.bind("<<ListboxSelect>>", self.dowhat)

        self.pageframe = ridgeFrame(self.main)
        self.pageframe.grid(column=1, row=0, sticky=(N, S, E, W))

        self.pagechoices = tk.StringVar()

        self.page = tk.Listbox(self.pageframe, listvariable=self.pagechoices, width=int(3*width/5), height=height)
        self.page.grid(column=0, row=0, sticky=(N, S, E, W))
        self.page.bind("<<ListboxSelect>>", self.dopage)

        self.resultframe = ridgeFrame(self.main)
        self.resultframe.grid(column=2, row=0, sticky=(N, S, E, W))

        self.results = tk.StringVar()

        self.result = tk.Listbox(self.resultframe, listvariable=self.results, width=int(4*width/5), height=height)
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

        self.numpages = tk.Entry(self.buttonframe, textvariable=self.numpagesvar)
        self.numpages.grid(column=1, row=1)

        self.ungridform()

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

        self.form: dat.formula | list = None
        self.formname = ""
        self.curpage = None

        self.root.mainloop()

    def gridform(self):
        self.genxls.grid()
        self.numpages.grid()
        self.numpageslabel.grid()

    def ungridform(self):
        self.genxls.grid_remove()
        self.numpages.grid_remove()
        self.numpageslabel.grid_remove()

    def dowhat(self, e):
        sel = self.what.curselection()

        if (len(sel) == 1):
            self.curpage = self.whatlist[sel[0]]
            self.pagechoices.set([n for n, _ in self.curpage])
            self.results.set([])
            self.reroll.grid_remove()
            self.ungridform()

    def dopage(self, e):
        sel = self.page.curselection()
        if (len(sel) == 1):
            self.formname, self.form = self.curpage[sel[0]]
            self.reroll.grid()

            if isinstance(self.form, dat.formula):
                self.gridform()
            else:
                self.ungridform()

            self.doreroll()

    def doreroll(self):
        if (self.form is not None):
            out = dat.gen3(self.form)
            match(out):
                case str():
                    self.results.set([self.formname + ": " + out])
                case list():
                    reout = []
                    for b, o in zip(self.form.labels, out):
                        reout.append(b + ": " + o)
                    self.results.set(reout)
                case _:
                    self.results.set([])

    def doxls(self):
        num = intnun(self.numpagesvar.get())
        num = num if num else 5
        dat.Manufacture(lambda: dat.general_generator(self.form), self.formname, num, self.form.split)


if __name__ == "__main__":
    ListMaster()
