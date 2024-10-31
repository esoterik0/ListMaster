import tkinter as tk
from tkinter import ttk, N, S, E, W
import gendata as dat


def ridgeFrame(content, **kwargs):
    return ttk.Frame(content, borderwidth=5, relief="ridge", **kwargs)


class ListMaster:
    def __init__(self, root):
        self.root = root
        self.main = ttk.Frame(root, padding=5)
        self.main.grid(column=0, row=0, sticky=(N, S, E, W))

        self.whatframe = ridgeFrame(self.main)
        self.whatframe.grid(column=0, row=0, sticky=(N, S))

        self.whatlist = [dat.All_tables, dat.Maze_Rats_pages, dat.formulas]
        whatchoices = ["All tables", "Maze Rats pages", "Formulas"]
        whatchoicevar = tk.StringVar(value=whatchoices)

        self.what = tk.Listbox(self.whatframe, listvariable=whatchoicevar)
        self.what.grid(column=0, row=0, sticky=(N, S, E, W))
        self.what.bind("<<ListboxSelect>>", self.dowhat)

        self.pageframe = ridgeFrame(self.main)
        self.pageframe.grid(column=1, row=0, sticky=(N, S))

        self.pagechoices = tk.StringVar()

        self.page = tk.Listbox(self.pageframe, listvariable=self.pagechoices)
        self.page.grid(column=0, row=0, sticky=(N, S, E, W))
        self.page.bind("<<ListboxSelect>>", self.dopage)
        self.pageframe.grid_remove()

        self.resultframe = ridgeFrame(self.main)
        self.resultframe.grid(column=2, row=0, sticky=(N, S, E, W))

        self.results = tk.StringVar()

        self.result = tk.Listbox(self.resultframe, listvariable=self.results)
        self.result.grid(column=0, row=0, sticky=(N, S))

        self.buttonframe = ttk.Frame(self.resultframe)
        self.buttonframe.grid(column=0, row=1, sticky=(E, W))

        self.reroll = ttk.Button(self.buttonframe, text="Re-Roll", command=self.doreroll)
        self.reroll.grid(column=0, row=0)

        self.genxls = ttk.Button(self.buttonframe, text="Generate .xls file", command=self.doxls)
        self.genxls.grid(column=1, row=0)
        self.genxls.grid_remove()
        self.resultframe.grid_remove()

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=1)
        self.main.columnconfigure(2, weight=1)
        self.whatframe.rowconfigure(0, weight=1)
        self.whatframe.columnconfigure(0, weight=1)
        self.pageframe.rowconfigure(0, weight=1)
        self.pageframe.columnconfigure(0, weight=1)
        self.resultframe.rowconfigure(0, weight=1)
        self.resultframe.columnconfigure(0, weight=1)
        self.buttonframe.rowconfigure(0, weight=1)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)

        self.form: dat.formula | list = None
        self.formname = ""
        self.page = None

    def dowhat(self):
        self.resultframe.grid_remove()
        self.pageframe.grid_remove()

        sel = self.what.curselection()

        if (len(sel) == 1):
            self.page = self.whatlist[sel[0]]
            self.pagechoices([n for n, _ in self.page])
            self.pageframe.grid()

    def dopage(self):
        self.resultframe.grid_remove()
        sel = self.page.curselection()
        if (len(sel) == 1):
            self.formname, self.form = self.page[sel[0]]
            self.resultframe.grid()

            if (type(self.form) is dat.formula):
                self.genxls.grid()
            else:
                self.genxls.grid_remove()

            self.doreroll()

    def doreroll(self):
        if (self.form is not None):
            match(self.form):
                case list():
                    self.results.set([dat.gen(self.form)])
                case dat.formula():
                    self.results.set(dat.gen_form(self.form))
                case None:
                    self.results.set([])

    def doxls(self):
        dat.Manufacture(lambda: dat.general_generator(self.form), self.formname, split=self.form.split)
        # self.resultframe.grid_remove()


root = tk.Tk()
lm = ListMaster(root)
root.mainloop()
