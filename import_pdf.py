"import pdf"

import re
import tkinter as tk
from enum import Enum
from tkinter import E, N, W, messagebox, ttk

from import_base import import_base
from ListEditPanel import ListEditPanel
from ListPanelLambda import ListPanelLambda
from PanelCom import PanelCom
from util import int_nun
import fitz as pdf


class Title_Enum(Enum):
    "Title Enum"
    TOP = "TOP"
    SEP = "SEP"

class Type_Enum(Enum):
    ALL = "ALL"  # all in one pdf chunk
    ONE = "ONE"  # one per pdf chunck

class import_pdf(import_base):
    "import pdf"
    def __init__(self, parent, file, panel, **kw_args):
        super().__init__(parent, **kw_args)
        self.panel: PanelCom = panel
        self.filename = file
        self.pagere = re.compile(r"(\d+)(?:-(\d+))?")
        self.lines = []

        self.frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.frame.columnconfigure(x, weight=1)

        fname, _, ext = self._get_title_path_ext_from_file(self.filename)

        self.pdf_list = ListPanelLambda(self.frame, None, self.process, self.drag)
        self.pdf_list.grid(row=0, column=1)
        self.pdf_list.title_var.set(f"{fname}.{ext}")

        self.lstpan = ListEditPanel(self.frame, self.winfo_toplevel())
        self.lstpan.grid(row=0, column=2)
        self.lstpan.title_var.set("")

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.columnconfigure(0, weight=1)
        for x in range(4):
            self.button_frame.rowconfigure(x, weight=1)
        self.button_frame.grid(row=0, column=0, sticky=(N, E, W))

        ########################################################
        # file label 'frame'
        butrow = 0

        self.file_label = tk.Label(self.button_frame, text=f"File: {file}")
        self.file_label.grid(row=butrow, column=0, sticky=(E, W))

        ########################################################
        # page 'frame'

        butrow += 1
        self.page_frame = ttk.Frame(self.button_frame)
        self.page_var = tk.StringVar()
        self.page_frame.rowconfigure(0, weight=1)
        for x in range(2):
            self.page_frame.columnconfigure(x, weight=1)
        self.page_frame.grid(row=butrow, column=0)

        self.page_label = tk.Label(self.page_frame, text="Page #: ")
        self.page_label.grid(row=0, column=0)

        self.page_entry = ttk.Entry(self.page_frame, textvariable=self.page_var)
        self.page_entry.grid(row=1, column=0)

        ########################################################
        # title option frame

        butrow += 1
        self.title_var = tk.StringVar()
        self.title_frame = ttk.Frame(self.button_frame)
        self.title_frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.title_frame.columnconfigure(x, weight=1)
        self.title_frame.grid(row=butrow, column=0, sticky=(E, W))

        self.title_label = ttk.Label(self.title_frame, text="Title is ")
        self.title_label.grid(row=0, column=0, sticky=(E, W))

        self.title_on_top = ttk.Radiobutton(
            self.title_frame,
            text="on top",
            variable=self.title_var,
            value=Title_Enum.TOP,
        )
        self.title_on_top.grid(row=0, column=1, sticky=(E, W))

        self.title_separate = ttk.Radiobutton(
            self.title_frame,
            text="Separate",
            variable=self.title_var,
            value=Title_Enum.SEP,
        )
        self.title_separate.grid(row=0, column=2, sticky=(E, W))

        ########################################################
        # Type Frame

        butrow += 1
        self.type_var = tk.StringVar()

        self.type_frame = ttk.Frame(self.button_frame)
        self.type_frame.rowconfigure(0, weight=1)
        for x in range(3):
            self.type_frame.columnconfigure(x, weight=1)
        self.type_frame.grid(row=butrow, column=0)

        self.type_label = ttk.Label(self.type_frame, text="List Type")
        self.type_label.grid(row=0, column=0, sticky=(E, W))

        self.type_all_button = ttk.Radiobutton(
            self.type_frame,
            text="All in one section",
            variable=self.type_var,
            value=Type_Enum.ALL.value,
        )
        self.type_all_button.grid(row=0, column=1, sticky=(E, W))

        self.type_one_button = ttk.Radiobutton(
            self.type_frame,
            text="One per section",
            variable=self.type_var,
            value=Type_Enum.ONE.value,
        )
        self.type_one_button.grid(row=0, column=2, sticky=(E, W))

        ########################################################
        # add title frame

        butrow += 1
        self.add_title = ttk.Button(
            self.button_frame,
            command=self.add_title,
            text="Add selection to title"
        )
        self.add_title.grid(row=butrow, column=0, sticky=(E, W))

        ########################################################
        # command frame

        butrow += 1
        self.command_frame = ttk.Frame(self.button_frame)
        self.command_frame.rowconfigure(0, weight=1)
        for x in range(2):
            self.command_frame.columnconfigure(x, weight=1)
        self.command_frame.grid(row=butrow, column=0)

        self.parse_butt = tk.Button(self.command_frame, text="Parse", command=self.parse)
        self.parse_butt.grid(row=0, column=0, sticky=(E,W))

        self.save_butt = tk.Button(self.command_frame, text="Save", command=self.save)
        self.save_butt.grid(row=0, column=1, sticky=(E,W))

    def parse(self):
        "parse the pdf"

        m = self.pagere.match(self.page_var.get().strip())

        if m is None:
            messagebox.showerror(
                message="You must enter the page number n or range n-m",
                title="No page number"
            )
            return

        start, end = m.groups()
        start, end = int_nun(start), int_nun(end)

        if end and end <= start:
            messagebox.showerror(
                message="The end must be after the start.",
                title="Invallid range"
            )
            return

        doc = pdf.open(self.filename)

        if end is None:
            self.parse_page(doc.load_page(start))
        else:
            for page in range(start, end+1):
                self.parse_page(doc.load_page(page))

        self.pdf_list.choices = [
            f"{s.count('\n')}: {s[:min(s.find('\n'), 80)]}"
            for s in self.lines
        ]
        self.pdf_list.update_lbox()

    def save(self):
        "save the list"

        if self.lstpan.choices:
            self.panel.insert_new_table(self.lstpan.title_var.get(), self.lstpan.choices)

        self.destroy()

    def parse_page(self, page: pdf.Page):
        "parse the page"
        for block in page.get_text_blocks():
            self.lines.append(block[4])

    def title(self, idx: int):
        "append to title"

    def drag(self, start: int, end: int):
        "add all in range to list"
        for idx in range(start, end+1):
            self.process(idx)

    def process(self, idx: int):
        "process a selection to add"