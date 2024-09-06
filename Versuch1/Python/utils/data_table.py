#
# Viewer for spectrometer files
# 30.09.2022
#

# pip install tkintertable
# pip install tksheet
# pip install openpyxl

import tkinter as tk
from tkinter import filedialog
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import utils.SpecReader_dataFile as dataFile
#from tksheet import Sheet


sTitle = 'Viewer for spectrometer files (V01.10.2022) by Ch. Heyn'

specScale =     []
specVals =      []


window = tk.Tk()
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
window.title(sTitle)
window_width = screenwidth-20; window_height = screenheight-100;
window.geometry( str(window_width)+'x'+str(window_height)+'+5+5')             # Window size

# Frames
frameMenue = tk.Frame(window)
frameTable = tk.Frame(window)
frameFig = tk.Frame(window)
frameMenue.pack(side='left', anchor='n', padx=10)
frameTable.pack(side='left',  anchor='n')
frameFig.pack(side='top',  anchor='w')
fig = Figure(figsize=(8,6))
plot = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, window)
toolbar = NavigationToolbar2Tk(canvas, frameFig)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)


# Button Load
def btnLoad_callback():
    FileName =  filedialog.askopenfilename(
        title = "Select file", filetypes = (("Data files","*.dat"),("all files","*.*")))
    loadSpec(FileName)
button_Load = tk.Button(master=frameMenue, text = "Load", width=12, height=2, command = btnLoad_callback)
button_Load.pack(side='top', pady=5)


# Button Save
def btnSave_callback():
    FileName = os.path.basename(os.path.splitext(dataFile.dataFileName)[0])+'_mod.dat'
    SaveFileName = tk.filedialog.asksaveasfilename(
        defaultextension='.dat', filetypes=[("data files", '*.dat')], title="Save filename", initialfile=FileName)
    saveSpec(SaveFileName)
button_Save = tk.Button(master=frameMenue, text = "Save", width=12, height=1, command = btnSave_callback)
button_Save.pack(side='top', pady=5)


# Button Quit
def btnQuit_callback():
    window.quit()
    window.destroy()
button_Quit = tk.Button(master=frameMenue, text = "Quit", width=12, command = btnQuit_callback)
button_Quit.pack(side='top', pady=15)


def loadIntoTable():
    #frameTable.grid_columnconfigure(0, weight = 1)
    #frameTablegrid_rowconfigure(0, weight = 1)
    frame = tk.Frame(window)
    frame.grid_columnconfigure(0, weight = 1)
    frame.grid_rowconfigure(0, weight = 1)
    #loadedData = pd.read_table("c:/Users/Christian/Downloads/Test.dat", delimiter = '  ')
    sheet = Sheet(frame,
        data = pd.read_table(
        # "c:/Users/Christian/Downloads/Test.dat", engine = 'python', delimiter = '  ').values.tolist())
        "Test.dat", engine = 'python', delimiter = '  ').values.tolist())
    sheet.enable_bindings()
    frame.grid(row = 0, column = 0, sticky = "nswe")
    sheet.grid(row = 0, column = 0, sticky = "nswe")


class demo(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(0, weight = 1)
        #loadedData = pd.read_table("c:/Users/Christian/Downloads/Test.dat", delimiter = '  ')
        self.sheet = Sheet(self.frame,
                           data = pd.read_table(
                                # "c:/Users/Christian/Downloads/Test.dat", engine = 'python', delimiter = '  ').values.tolist())
                                "Test.dat", engine = 'python', delimiter = '  ').values.tolist())
        self.sheet.enable_bindings()
        self.frame.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")


#app = demo()
#app.mainloop()


def clearSpec():
    global specScale, specVals
    specScale = []; specVals  = []


def loadSpec(FileName):
    global specScale, specVals
    data = dataFile.importDataFile(FileName)
    SpecScale = np.array(data)[ : , 0]
    SpecVals =  np.array(data)[ : , 1]
    fig.clf()
    fig.add_subplot(111).plot(SpecScale, SpecVals)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)
    window.title(sTitle+': '+os.path.basename(dataFile.dataFileName))


def saveSpec(SaveFileName):
    dataFile.saveDataFile(dataFile.data,SaveFileName)


window.mainloop()
