from multiprocessing.sharedctypes import Value
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
import pandas as pd
from time import sleep

root = Tk()
root.title("EPT Processor")
root.geometry("400x300")

option = IntVar()
option.set("1")
progress = IntVar()

def show():
    Label(root,
        text=root.filename).pack()

def selectOption():
    Label(root,
        text="Select option to process file").place(x=40, y=70)

    Radiobutton(root, 
        text="All Rows",
        value=1,
        variable=option).place(x=40, y=120)

    Radiobutton(root, 
        text="Select Rows by Municipio",
        value=2,
        variable=option).place(x=40, y=150)

    Button(root,
        text="Next",
        command=show).place(x=300, y=150)
    
    Progressbar(root,
        orient=HORIZONTAL,
        length=300,
        variable=progress,
        mode='determinate').place(x=40, y=200)

# root.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("xlsx files", "*.xlsx"),("all files", "*.*")))
selectOption()
root.mainloop()
