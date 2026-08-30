"the page panel: shows what pages are in the top level category chosen by the what panel."

import tkinter as tk
from tkinter import E, N, S, W, messagebox, ttk
from tkinter.simpledialog import askstring

from enums import ItemColor, ItemType, State, table
from gendata import Formula, MetaFormula
from ListTitlePanelABC import ListTitlePanelABC
from PanelCom import PanelCom


class PagePanel(ListTitlePanelABC):  # pylint: disable=too-many-ancestors,too-many-instance-attributes
    "generates the page frame, for choosing, inspecting, or editing which 'page', formula or table"

    def __init__(self, parent: PanelCom, **kwargs):
        super().__init__(parent, drag=False, **kwargs)
        self._parent: PanelCom = parent
        self.filter_type = None

        self.lbox.bind("<Double-1>", self.do_double_page)
        self.lbox.bind("<F2>", self.do_edit_item)

        self.title_var.set("Page")

        # buttons for ROLL mode
        self.button_frame_roll = ttk.Frame(self)
        self.button_frame_roll.grid(column=0, row=self.ROW, sticky=(E, W))

        # radio button set
        self.filter_var = tk.StringVar()
        self.list_filter = ttk.Radiobutton(
            self.button_frame_roll,
            text="List",
            variable=self.filter_var,
            value=ItemType.LIST.value,
            command=self.set_filter
        )
        self.list_filter.grid(column=0, row=0, sticky=(E, W))
        self.form_filter = ttk.Radiobutton(
            self.button_frame_roll,
            text="Formula",
            variable=self.filter_var,
            value=ItemType.FORM.value,
            command=self.set_filter
        )
        self.form_filter.grid(column=0, row=1, sticky=(E, W))
        self.meta_filter = ttk.Radiobutton(
            self.button_frame_roll,
            text="MetaFormula",
            variable=self.filter_var,
            value=ItemType.META.value,
            command=self.set_filter
        )
        self.meta_filter.grid(column=1, row=0, sticky=(E, W))
        self.no_filter = ttk.Radiobutton(
            self.button_frame_roll,
            text="None",
            variable=self.filter_var,
            value=ItemType.NONE.value,
            command=self.set_filter
        )
        self.no_filter.grid(column=1, row=1, sticky=(E, W))

        # buttons for EDIT mode
        self.button_frame_edit = ttk.Frame(self)
        self.button_frame_edit.grid(column=0, row=self.ROW+1, sticky=(E, W))
        self.button_frame_edit.grid_remove()

        self.new_meta = ttk.Button(
            self.button_frame_edit,
            text="New Meta Formula",
            command=self.do_new_meta,
        )
        self.new_meta.grid(column=0, row=2, sticky=(N, S, E, W))

        self.new_form = ttk.Button(
            self.button_frame_edit, text="New Formula",
            command=self.do_new_form,
        )
        self.new_form.grid(column=0, row=1, sticky=(N, S, E, W))

        self.new_list = ttk.Button(
            self.button_frame_edit,
            text="New List",
            command=self.do_new_list
        )
        self.new_list.grid(column=0, row=0, sticky=(N, S, E, W))

        self.add_item = ttk.Button(
            self.button_frame_edit,
            text="Copy Item Name",
            command=self.do_copy_item
        )
        self.add_item.grid(column=1, row=1, sticky=(N, S, E, W))

        self.edit_item = ttk.Button(
            self.button_frame_edit,
            text="Edit Item",
            command=self.do_edit_item
        )
        self.edit_item.grid(column=1, row=0, sticky=(N, S, E, W))

        self.insert_item = ttk.Button(
            self.button_frame_edit,
            text="Insert Item",
            command=self.do_insert_item
        )
        self.insert_item.grid(column=1, row=2, sticky=(N, S, E, W))

        self.button_frame_edit.rowconfigure(0, weight=1)
        self.button_frame_edit.rowconfigure(1, weight=1)
        self.button_frame_edit.columnconfigure(0, weight=1)
        self.button_frame_edit.columnconfigure(1, weight=1)

        self.button_frame_roll.columnconfigure(0, weight=1)
        self.button_frame_roll.columnconfigure(1, weight=1)
        self.button_frame_roll.rowconfigure(0, weight=1)
        self.button_frame_roll.rowconfigure(1, weight=1)
        self.button_frame_roll.rowconfigure(2, weight=1)

        self._cur_page = None
        self._filter_page = None
        self._name = None

    def set_filter(self):
        "handles the filter radio button"
        match(self.filter_var.get()):  # _var has a string ...
            case ItemType.META.value:  # ... so we use .value to match against
                self.filter_type = MetaFormula
            case ItemType.FORM.value:
                self.filter_type = Formula
            case ItemType.LIST.value:
                self.filter_type = list
            case _:
                self.filter_type = None

        self.set_page(self._name, self._cur_page)

    def accept_edit(self, newtext: str) -> bool:
        "validate and accept edit or reject it"
        if self.last_selection is None:
            return # ignore broken edits

        if self.last_selection >= len(self.choices):
            return

        name = self.choices[self.last_selection]
        if newtext == "":
            if name == "":  # skip spurrious adds
                del self._cur_page[self.last_selection]
            elif not self._parent.check_delete_from_all(name):
                del self._cur_page[self.last_selection]
                self._parent.set_result_item()  # results might still be displaying this
            else:
                self._parent.set_result_item()  # deleted by delete from all
        elif self._is_safe(newtext):
            if name == "":  # new entry
                self._parent.add_to_all(tup := (newtext, self._cur_page[self.last_selection][1]))
                self._cur_page[self.last_selection] = tup
                self.set_page(self._name, self._cur_page)
            elif name == newtext:  # skip unchanged entries
                return
            elif self._parent.name_available(newtext):
                self._parent.rename(name, newtext) # change all
            else:
                self.edit.destroy()
                self.edit = None
                messagebox.showerror(
                    title="Name collision",
                    message=f"The chosen name: {newtext} already exists"
                )
                return
        else:
            self.edit.destroy()
            self.edit = None
            messagebox.showerror(
                title="Invallid characters",
                message="Your entry contains invallid characters\n"
                     "the only characters allowed are\n"
                     "'a-z','A-z','0-9','.,|&:+-()[] '",
            )
            return

        self.set_page(self._name, self._cur_page)

    def set_page(self, name: str | None, lst: list | None, sort = True):
        "sets the contents of the page panel"
        self._name = name
        if self._name:
            self.title_var.set(f'Page "{name}"')
        else:
            self.title_var.set("Page")
        self.last_selection = None
        if lst is None:
            self._cur_page = None
            self.choices = []
            self.update_lbox()
            self.grid_set()
            return

        if sort:
            lst.sort(key = lambda x: x[0])
        self._cur_page = lst
        self._filter_page = self._filter()
        self.choices = [n[0] for n in self._filter_page]
        self.update_lbox()
        for i, pg in enumerate(self._filter_page):
            _, entry = pg
            match (entry):
                case (MetaFormula()):
                    self.lbox.itemconfig(index=i, background=ItemColor.META.value)
                case (Formula()):
                    self.lbox.itemconfig(index=i, background=ItemColor.FORM.value)
                case (list()):
                    self.lbox.itemconfig(index=i, background=ItemColor.LIST.value)
        self.grid_set()

    def set_state(self):
        "set state handler called when _parent changes state"
        self.ungrid_set()
        self.grid_set()

    def ungrid_set(self):
        "removes widgets"
        self.button_frame_edit.grid_remove()

    def grid_set(self):
        "adds widgets"
        if self._parent.state == State.EDIT:
            self.button_frame_edit.grid()

    def do_lbox_sel(self, *args):  # pylint: disable=unused-argument
        "handles the 'page' column to choose which table, page, or formula to generate from; triggers re-roll"
        if not self._cur_page:
            return

        if self._sel() is not None:  # allow 0 to pass inspection
            if self._parent.state == State.ROLL:
                self._parent.set_result_item(self._cur_page[self.last_selection])

    def do_double_page(self, e):  # pylint: disable=unused-argument
        "handles double click on the 'page' column to choose what to edit"
        if not self._cur_page:
            return

        if self._sel() is not None:
            if self._parent.state == State.EDIT:
                self._parent.set_result_item(self._cur_page[self.last_selection])

    def do_edit_item(self, *args):  # pylint: disable=unused-argument
        "handle edit item button, and double click"
        if not self._cur_page:
            return "continue"

        if self._sel() is not None:
            return self._start_edit(self.choices[self.last_selection])

        return "continue"

    def _finish_start_edit(self, item: tuple[str, table | Formula | MetaFormula], prompt: str):
        "common code to complete starting an edit"
        self._cur_page.append(item)
        self.set_page(self._name, self._cur_page, False)
        self.last_selection = len(self._filter_page)-1
        self.look()
        return self._start_edit(prompt)

    def _check_page(self):
        if self._cur_page is None:
            messagebox.showerror(
                title="Missing Collection",
                message="You must select a collection to add items to."
            )
            return True
        return False

    def do_new_form(self):
        "handle new Form button"
        if self._check_page():
            return "continue"

        if self.filter_type and self.filter_type != Formula:
            return "continue"

        return self._finish_start_edit(("", Formula([], [], "")), "New Formula")

    def do_new_list(self):
        "handle new list button"
        if self._check_page():
            return "continue"

        if self.filter_type and self.filter_type != list:
            return "continue"

        return self._finish_start_edit(("", []), "New List")

    def do_new_meta(self):
        "handle new MetaFormula button"
        if self._check_page():
            return "continue"

        if self.filter_type and self.filter_type != MetaFormula:
            return "continue"

        return self._finish_start_edit(("", MetaFormula([], [], "")), "New MetaFormula")

    def do_copy_item(self):
        "handle add item button"
        if not self._cur_page or self.last_selection is None:
            messagebox.showerror(
                title="Missing Collection",
                message="You must select a collection to copy an item from."
            )
            return
        idx, tab = self._parent.get_name_index(self.choices[self.last_selection])
        if idx is None:
            return
        self._parent.do_clipboard(self._parent.get_name(tab))

    def _filter(self):
        "filter the data"
        if self.filter_type is None:
            return self._cur_page

        return [n for n in self._cur_page if isinstance(n[1], self.filter_type)]

    def do_insert_item(self):
        "insert an item into our list"
        newitem = askstring("Insert Item", "Name of the item; {} are optional, no duplicates").strip()

        # strip {}
        if newitem[0] == "{":
            newitem = newitem[1:]
        if newitem[-1] == "}":
            newitem = newitem[:-1]

        if not self._is_safe(newitem):
            return # name must be safe

        if self._parent.name_available(newitem):
            return # name must exist

        if any(x[0] == newitem for x in self._cur_page):
            return # cannot have duplicates in the same page!

        _, tab = self._parent.get_name_index(newitem)
        if tab is not None:
            self._cur_page.append((newitem, tab))
            self.set_page(self._name, self._cur_page)

    def export(self, path: str):
        "export a table"
        if self.last_selection is None:
            messagebox.showerror(
                title="Missing Selection",
                text="Nothing has been selected for export\n"
                     "Please choose something on the page panel",
            )
            return

        title, tbl = self._cur_page[self.last_selection]
        with open(f"{path}/{title}.txt", "w", encoding="utf-8") as f:
            lines = [
                f"{iota}. {self._parent.get_name(x)}"
                for iota, x in enumerate(tbl, 1)
            ]
            print(*lines, sep='\n', end='\n', file=f)
