"code to edit a listbox entry in place (in situ)"
import tkinter as tk
from typing import Callable, Literal

def start_edit(
    box: tk.Listbox, # listbox to use
    index: int, # index to use
    accept: Callable[[str], None], # callback for acceptance
    text: str | None = None # optional string instead of looking up by index
) -> Literal["break"]:
    "start an in place edit for a list box"

    def accept_edit(event):
        "accept and finish an in place edit"
        accept(event.widget.get())
        event.widget.destroy()

    def cancel_edit(event):
        "cancel an in place edit"
        event.widget.destroy()

    if text is None:
        text = box.get(index)
    entry = tk.Entry(box, borderwidth=0, highlightthickness=1)

    entry.bind("<Return>", accept_edit)
    entry.bind("<Escape>", cancel_edit)

    entry.insert(0, text)
    entry.selection_from(0)
    entry.selection_to("end")
    entry.place(relx=0, y=box.bbox(index)[1], relwidth=1, width=-1)
    entry.focus_set()
    entry.grab_set()

    return entry # allow's external cancelation
