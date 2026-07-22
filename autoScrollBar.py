from tkinter import ttk

class AutoScrollbar(ttk.Scrollbar):
    "A scrollbar that hides itself if it's not needed. Only works if you use the grid geometry manager."
    def set(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.grid_remove() # Hide if not needed
        else:
            self.grid()       # Show if needed
        super().set(first, last)