"module window/dialog, to import a text file"

import tkinter as tk
from tkinter import E, IntVar, N, S, StringVar, W, messagebox, ttk

from import_base import ListType, TitleType, import_base
from ListEditPanel import ListEditPanel
from PanelCom import PanelCom


class import_txt(import_base):  # pylint: disable=too-many-instance-attributes
    "window/dialog to import a text file"
    def __init__(self, parent, file, panel: PanelCom, **kw_args):
        super().__init__(parent, **kw_args)
        self.panel: PanelCom = panel
        self.filename = file
        self.lists: ListEditPanel = []
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.frame =  ttk.Frame(self)
        self.frame.grid(row=0, column=0, sticky=(E, N, S, W))
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.button_frame = ttk.Frame(self.frame)
        for i in range(10):
            self.button_frame.rowconfigure(i, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.grid(row=0, column=0, sticky=(E, N, S, W))

        self.type_var = IntVar(value=ListType.SINGLE.value)

        self.type_radio_single = ttk.Radiobutton(
            self.button_frame,
            text="Single List",
            variable=self.type_var,
            value=ListType.SINGLE.value,
            command=self.arity
        )
        self.type_radio_single.grid(row=0, column=0)

        self.type_radio_multi = ttk.Radiobutton(
            self.button_frame,
            text="Multiple Lists",
            variable=self.type_var,
            value=ListType.MULTI.value,
            command=self.arity
        )
        self.type_radio_multi.grid(row=0, column=1)
        self.type_var.set(ListType.SINGLE.value)

        self.list_delim_var = StringVar()
        self.list_delim = ttk.Entry(self.button_frame, textvariable=self.list_delim_var)
        self.list_delim.grid(row=1,column=0, sticky=(E, W))

        self.title_delim_var = StringVar()
        self.title_delim = ttk.Entry(self.button_frame, textvariable=self.title_delim_var)
        self.title_delim.grid(row=2,column=0, sticky=(E, W))

        self.title_use_same_delim_var = IntVar(value=TitleType.FILE.value)

        self.title_same = ttk.Radiobutton(
            self.button_frame,
            text = "title delimeter is same",
            value=TitleType.SAME.value,
            variable=self.title_use_same_delim_var
        )
        self.title_same.grid(row=3, column=0)

        self.title_diff = ttk.Radiobutton(
            self.button_frame,
            text = "title delimeter is different",
            value=TitleType.DIFF.value,
            variable=self.title_use_same_delim_var
        )
        self.title_diff.grid(row=4, column=0)

        self.title_none = ttk.Radiobutton(
            self.button_frame,
            text = "There is no title delimeters; title is first line",
            value=TitleType.NONE.value,
            variable=self.title_use_same_delim_var
        )
        self.title_none.grid(row=5, column=0)

        self.title_miss = ttk.Radiobutton(
            self.button_frame,
            text = "There are no titles",
            value=TitleType.MISS.value,
            variable=self.title_use_same_delim_var
        )
        self.title_miss.grid(row=6, column=0)

        self.title_file = ttk.Radiobutton(
            self.button_frame,
            text = "Filename is the title",
            value=TitleType.FILE.value,
            variable=self.title_use_same_delim_var
        )
        self.title_file.grid(row=7, column=0)

        self.parse_button = ttk.Button(
            self.button_frame,
            text=f"Parse text file: {file}",
            command=self.parse
        )
        self.parse_button.grid(row=8,column=0)

        self.save_button = ttk.Button(
            self.button_frame,
            text="save tables",
            command=self.save
        )
        self.save_button.grid(row=9, column=0)

        self.arity()

    def arity(self):
        "multi or single"
        match(self.type_var.get()):
            case ListType.SINGLE.value:
                self.list_delim.grid_remove()
                self.title_delim.grid_remove()
                self.title_same.grid_remove()
                self.title_diff.grid_remove()
                self.title_none.grid_remove()
                self.title_miss.grid_remove()
                self.title_file.grid()
                self.title_use_same_delim_var.set(TitleType.FILE.value)

            case ListType.MULTI.value:
                self.list_delim.grid()
                self.title_delim.grid()
                self.title_same.grid()
                self.title_diff.grid()
                self.title_none.grid()
                self.title_miss.grid()
                self.title_file.grid_remove()
                self.title_use_same_delim_var.set(TitleType.SAME.value)

    def parse(self):
        "parse the text file and make tables"
        title, _, _ = self._get_title_path_ext_from_file(self.filename)
        l: ListEditPanel
        for l in self.lists:
            l.grid_remove()
            l.destroy()

        self.lists = []

        match(self.type_var.get()):
            case ListType.SINGLE.value:
                with open(self.filename, "r", encoding="utf-8") as f:
                    lst = f.readlines()

                lst = self._filter_list(lst)
                self.frame.columnconfigure(1, weight=1)
                edit_panel = ListEditPanel(self, self.winfo_toplevel(), 1)
                self.lists.append(edit_panel)
                edit_panel.grid(row=0, column=1)
                edit_panel.title_var.set(title)
                edit_panel.choices = lst

            case ListType.MULTI.value:
                lstdel = self.list_delim_var.get()
                titledel = self.title_use_same_delim_var.get()
                title_needed = True
                match(self.title_use_same_delim_var.get()):
                    case TitleType.SAME.value:
                        titledel = lstdel
                    case TitleType.DIFF.value:
                        pass
                    case TitleType.NONE.value:
                        titledel = None
                    case TitleType.MISS.value:
                        title_needed = None

                lst = []
                with open(self.filename, "r", encoding="utf-8") as f:
                    lst = f.readlines()

                lst = self._filter_list(lst)
                title = ""
                newlst = []

                while lst:
                    if title_needed:
                        title = lst[0]
                        lst = lst[1:]
                        if titledel:  # if we have a title delimeter
                            while lst and lst[0].find(titledel) < 0:
                                lst = lst[1:]
                            lst = lst[1:]  # get rid of the delimeter
                        title_needed = False
                        continue
                    while lst and lst[0].find(lstdel) < 0:
                        newlst.append(lst[0])
                        lst = lst[1:]
                    lst = lst[1:] # get rid of the delimeter

                    col = len(self.lists)
                    self.frame.columnconfigure(col, weight=1)
                    edit_panel = ListEditPanel(self, self.winfo_toplevel(), col)
                    self.lists.append(edit_panel)
                    edit_panel.grid(row=0, column=col)
                    edit_panel.title_var.set(title)
                    edit_panel.choices = newlst

                    title = ""
                    newlst = []
                    if title_needed is False:  # don't change if None
                        title_needed = True

                if newlst:
                    edit_panel = ListEditPanel(self, self.winfo_toplevel())
                    self.lists.append(edit_panel)
                    col = len(self.lists)
                    self.frame.columnconfigure(col, weight=1)
                    edit_panel.grid(row=0, column=col)
                    edit_panel.title_var.set(title)
                    edit_panel.choices = newlst

        edit_panel.update_lbox()

    def save(self):
        "save the list"

        if not self.lists:
            messagebox.showerror(
                message="No tables found to save.",
                title="Tables have not been parsed"
            )  # consider merging the tables.
            return

        panel: ListEditPanel
        for panel in self.lists:
            self.panel.insert_new_table(panel.title_var.get(), panel.choices)

        self.destroy( )
