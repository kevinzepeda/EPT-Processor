from tkinter import *
from tkinter import filedialog
import pandas as pd

root = Tk()
root.title("EPT Processor")
root.geometry("400x400")

allRows = IntVar()
selectedRows = IntVar()


def show():
    Label(root,
        text="All Rows: " + allRows.get()).pack()
    Label(root,
        text="Select Rows" + selectedRows.get()).pack()

# root.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("xlsx files", "*.xlsx"),("all files", "*.*")))

Checkbutton(root, 
    text="All Rows",
    variable=allRows).pack()

Checkbutton(root, 
    text="Select Rows by Municipio",
    variable=allRows).pack()

Button(root,
    text="Next",
    command=show)

root.mainloop()