"dialog to import lists from pdf files"

import re
import tkinter as tk
from enum import Enum
from tkinter import E, N, W, messagebox, ttk

import pymupdf as pdf

from import_base import import_base
from ListEditPanel import ListEditPanel
from ListPanelLambda import ListPanelLambda
from PanelCom import PanelCom
from util import int_nun


class Title_Enum(Enum):
    "Title Enum"
    TOP = "TOP"  # title is at the top of the chunk
    SEP = "SEP"  # title is in a separate chunk

class Type_Enum(Enum):
    "Type Enum"
    ALL = "ALL"  # all in one pdf chunk
    ONE = "ONE"  # one per pdf chunck

class import_pdf(import_base):  # pylint: disable=too-many-instance-attributes
    "UI & code to import lists from pdf files"
    def __init__(self, parent, file, panel, **kw_args):
        super().__init__(parent, **kw_args)
        self.title("Import PDF")
        self.panel: PanelCom = panel
        self.filename: str = file
        self.file_disp: int = 42
        self.pady = 3
        self.pagere = re.compile(r"(\d+)(?:-(\d+))?")
        self.newre = re.compile("\n")
        self.lines = []

        # n.b. some of this stuff may not need to be saved in self. once it has
        # been added/gridded it shouldn't get garbage collected, but we save
        # everything just in case.

        self.frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.frame.columnconfigure(x, weight=1)

        fname, _, ext = self._get_title_path_ext_from_file()

        self.pdf_list = ListPanelLambda(self.frame, None, self.double, self.drag)
        self.pdf_list.grid(row=0, column=1)
        self.pdf_list.title_var.set(f"{fname}.{ext}")

        self.lstpan = ListEditPanel(self.frame, self.winfo_toplevel())
        self.lstpan.grid(row=0, column=2)
        self.lstpan.title_var.set("")

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.columnconfigure(0, weight=1)
        for x in range(6):
            self.button_frame.rowconfigure(x, weight=1)
        self.button_frame.grid(row=0, column=0, sticky=(N, E, W))

        # add frames to button frame
        self._file_frame_foo(0)
        self._page_frame_foo(1)
        self._title_frame_foo(2)
        self._type_frame_foo(3)
        self._add_title_frame_foo(4)
        self._command_frame_foo(5)
        self.title_type_checked()

    # def _add_sep(self, buttrow: int):
    #     "add a separator"
    #     # sep = ttk.Separator(self.button_frame, orient="horizontal")
    #     # sep.grid(row=buttrow, column=0, sticky=(E, W))
    #     sep = tk.Frame(self.button_frame, bd=10, relief='sunken', height=2, background="black")
    #     sep.grid(row=buttrow, column=0, sticky=(E,W),pady=6)

    def _file_frame_foo(self, butrow):
        "construct the file frame"
        filename = self.filename
        if len(filename) > self.file_disp:
            filename = "..."+filename[-self.file_disp:]
        self.file_label = tk.Label(self.button_frame, text=f"File: {filename}")
        self.file_label.grid(row=butrow, column=0, sticky=(E, W), pady=self.pady)

    def _page_frame_foo(self, butrow):
        "construct the page frame"
        self.page_frame = ttk.Frame(self.button_frame)
        self.page_var = tk.StringVar()
        self.page_frame.rowconfigure(0, weight=1)
        for x in range(2):
            self.page_frame.columnconfigure(x, weight=1)
        self.page_frame.grid(row=butrow, column=0, pady=self.pady)

        self.page_label = tk.Label(self.page_frame, text="Page #: ")
        self.page_label.grid(row=0, column=0,sticky=(E, W))

        self.page_entry = ttk.Entry(
            self.page_frame,
            textvariable=self.page_var,
            command=self.parse
        )
        self.page_entry.grid(row=0, column=1, sticky=(E, W))


    def _title_frame_foo(self, butrow):
        "construct title option frame"
        self.title_var = tk.StringVar()
        self.title_frame = ttk.Frame(self.button_frame)
        self.title_frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.title_frame.columnconfigure(x, weight=1)
        self.title_frame.grid(row=butrow, column=0, pady=self.pady)

        self.title_label = ttk.Label(self.title_frame, text="Title is ")
        self.title_label.grid(row=0, column=0, sticky=(E, W))

        self.title_on_top = ttk.Radiobutton(
            self.title_frame,
            text="on top",
            variable=self.title_var,
            value=Title_Enum.TOP.value,
            command=self.title_type_checked
        )
        self.title_on_top.grid(row=0, column=1, sticky=(E, W))

        self.title_separate = ttk.Radiobutton(
            self.title_frame,
            text="Separate",
            variable=self.title_var,
            value=Title_Enum.SEP.value,
            command=self.title_type_checked
        )
        self.title_separate.grid(row=0, column=2, sticky=(E, W))

        self.title_var.set(Title_Enum.TOP.value)

    def _type_frame_foo(self, butrow):
        "construct list type frame"
        self.type_var = tk.StringVar()

        self.type_frame = ttk.Frame(self.button_frame)
        self.type_frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.type_frame.columnconfigure(x, weight=1)
        self.type_frame.grid(row=butrow, column=0, pady=self.pady)

        self.type_label = ttk.Label(self.type_frame, text="List Type")
        self.type_label.grid(row=0, column=0, sticky=(E, W))

        self.type_all_button = ttk.Radiobutton(
            self.type_frame,
            text="All in one section",
            variable=self.type_var,
            value=Type_Enum.ALL.value,
            command=self.list_type_checked
        )
        self.type_all_button.grid(row=0, column=1, sticky=(E, W))

        self.type_one_button = ttk.Radiobutton(
            self.type_frame,
            text="One per section",
            variable=self.type_var,
            value=Type_Enum.ONE.value,
            command=self.list_type_checked
        )
        self.type_one_button.grid(row=0, column=2, sticky=(E, W))

        self.type_var.set(Type_Enum.ALL.value)

    def _add_title_frame_foo(self, butrow):
        "construct add title frame"
        self.add_title_frame = ttk.Frame(self.button_frame)
        self.add_title_frame.rowconfigure(0, weight=1)
        for x in range(2):
            self.add_title_frame.columnconfigure(x, weight=1)
        self.add_title_frame.grid(row=butrow, column=0, pady=self.pady)

        self.add_title_butt = ttk.Button(
            self.add_title_frame,
            command=self.add_to_title,
            text="Add to title"
        )
        self.add_title_butt.grid(row=0, column=0, sticky=(E, W))
        self.set_title_butt = ttk.Button(
            self.add_title_frame,
            command=self.set_title,
            text="set title"
        )
        self.set_title_butt.grid(row=0, column=1, sticky=(E, W))

    def _command_frame_foo(self, butrow):
        "constuct command frame"
        self.command_frame = ttk.Frame(self.button_frame)
        self.command_frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.command_frame.columnconfigure(x, weight=1)
        self.command_frame.grid(row=butrow, column=0, pady=self.pady)

        self.parse_butt = ttk.Button(self.command_frame, text="Parse PDF", command=self.parse)
        self.parse_butt.grid(row=0, column=0, sticky=(E,W))

        self.save_butt = ttk.Button(self.command_frame, text="Save List", command=self.save)
        self.save_butt.grid(row=0, column=1, sticky=(E,W))

        self.save_quit_butt = ttk.Button(self.command_frame, text="Save & Quit", command=self.save_quit)
        self.save_quit_butt.grid(row=0, column=2, sticky=(E, W))

    def title_type_checked(self):
        "hide buttons based on title handling type"
        match(self.title_var.get()):
            case Title_Enum.SEP.value:
                self.add_title_frame.grid()
            case Title_Enum.TOP.value:
                self.add_title_frame.grid_remove()

    def list_type_checked(self):
        "hide buttons based on list type"
        match(self.type_var.get()):
            case Type_Enum.ALL.value:
                self.title_on_top.state(["!disabled"])
            case Type_Enum.ONE.value:
                self.title_var.set(Title_Enum.SEP.value)
                self.title_on_top.state(["disabled"])
                self.title_type_checked()


    def parse(self):
        "parse the pdf file and build the table"

        m = self.pagere.match(self.page_var.get().strip())

        if m is None:
            messagebox.showerror(
                message="You must enter the page number n or range n-m",
                title="No page number"
            )
            return

        self.lines = []  # reset lines
        self.lstpan.choices = []
        self.lstpan.title_var.set("")
        self.lstpan.update_lbox()

        start, end = m.groups()
        # if we have a match, start will be valid
        start, end = int_nun(start)-1, int_nun(end)

        if end:
            end -= 1

        if end and end <= start:
            messagebox.showerror(
                message="The end must be after the start.",
                title="Invallid range"
            )
            return

        doc = pdf.open(self.filename)

        if end is None:
            # single page
            self.parse_page(doc.load_page(start))
        else:
            # multiple pages
            for page in range(start, end+1):
                self.parse_page(doc.load_page(page))

        self.pdf_list.choices = [
            f"{s.count('\n')}: {s[:min(s.find('\n'), self.Title_Len)]}"
            for s in self.lines
        ]
        self.pdf_list.update_lbox()

    def save_quit(self):
        "save table/list and quit"
        if self._save():
            self.destroy()

    def save(self):
        "save the list"
        if self._save():
            self.lstpan.choices = []
            self.lstpan.title_var.set("")
            self.lstpan.update_lbox()

    def _save(self) -> bool:
        "save the list"
        if self.lstpan.choices:
            return self.panel.insert_new_table(
                self.lstpan.title_var.get()[:self.Title_Len],
                sorted(self.lstpan.choices)
            )

        return False

    def parse_page(self, page: pdf.Page):
        "parse the page"
        # block ~=(x0, y0, x1, y1, "lines in the block", block_no, block_type)
        for block in page.get_text("blocks"):  # TextPage.extractBLOCKS()
            if block[6] == 0:  # get text boxes only
                self.lines.append(block[4])  # get the text

    def add_to_title(self):
        "add to title"
        self._title(self.pdf_list.last_selection)

    def set_title(self):
        "add to title"
        self._title(self.pdf_list.last_selection, False)

    def _title(self, idx: int, add=True):
        "append to title"
        match(self.title_var.get()):
            case Title_Enum.TOP.value:
                # n.b. should never come up because we hide the button in this mode
                messagebox.showerror(
                    message="This button does not work in Title on top mode.",
                    title="Invallid combination"
                )
                return
            case Title_Enum.SEP.value:
                # remove newlines
                new_title = " ".join(self.newre.split(self.lines[idx]))

                if add:  # append the title
                    new_title = " ".join([self.lstpan.title_var.get(), new_title])

                # set the title
                self.lstpan.title_var.set(new_title)
                del self.lines[idx]
                del self.pdf_list.choices[idx]
                self.pdf_list.update_lbox()


    def drag(self, start: int, end: int):
        "add all in range to list via dragging"

        if start == end:
            return

        if start > end:
            start, end = end, start

        for idx in range(start, end+1):
            self._process(idx)

        # remove processed
        for idx in range(start, end+1):
            del self.pdf_list.choices[idx]
            del self.lines[idx]

        self.pdf_list.update_lbox()

    def double(self, idx: int):
        "double click to add to list"
        self._process(idx)
        # deleteing the item caused drag to see two different indexes
        # as the items have shifted, or dissapeared,
        # checking the distance moved between events now
        del self.pdf_list.choices[idx]
        del self.lines[idx]
        self.pdf_list.update_lbox()

    def _process(self, idx: int):
        "process a selection to add to the list"

        top_title = self.title_var.get() == Title_Enum.TOP.value

        match(self.type_var.get()):
            case Type_Enum.ALL.value:
                new_vals = self._filter_list(self.newre.split(self.lines[idx]))

                # only add the title if choices are empty
                if top_title and not self.lstpan.choices:
                    self.lstpan.title_var.set(new_vals[0])
                    new_vals = new_vals[1:]  # shave off the title

                # add the items to the list
                self.lstpan.choices = self.lstpan.choices + new_vals

            case Type_Enum.ONE.value:
                if top_title:
                    messagebox.showerror(
                        message="Title on top is in compatible with one per section",
                        title="Invallid combination"
                    )
                    return

                new_value = " ".join(self.newre.split(self.lines[idx]))
                new_value = "".join(self.numcut.split(new_value).strip())
                self.lstpan.choices.append(new_value)

        self.lstpan.update_lbox()
