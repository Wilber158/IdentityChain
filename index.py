import eel
import tkinter as tk
from tkinter import filedialog

@eel.expose
def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()


eel.init("web")
eel.start("main.html")