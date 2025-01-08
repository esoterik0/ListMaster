"start.py: starts the ListMaster Program"
import tkinter as tk

from listmaster import ListMaster

if __name__ == "__main__":
    root = tk.Tk()
    ListMaster(root)
    root.mainloop()
