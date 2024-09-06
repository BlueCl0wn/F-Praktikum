#
# Viewer for data files
#


import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import utils.data_Spec as spec
import utils.data_Plot as dataPlot
import utils.data_Fit as fit


sTitle = 'Viewer for spectrometer files (V24.06.2023) by Ch. Heyn'


################################################################################
# Main window

window = tk.Tk()
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
window.title(sTitle)
window_width = screenwidth-200; window_height = screenheight-100;
window.geometry( str(window_width)+'x'+str(window_height)+'+5+5')             # Window size


################################################################################
# Frames

frameMenue = tk.Frame(window)
frameFig = tk.Frame(window)
frameMenue.pack(side='left', anchor='n', padx=10)
frameFig.pack(side='top',  anchor='w')
fig = Figure(figsize=(8,8))
plot = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, window)
toolbar = NavigationToolbar2Tk(canvas, frameFig)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)


################################################################################
# Mouse click into spectrum

specClickx =        0
specClicky =        0
cutLeftClick =      False
cutRightClick =     False
normalizeClick =    False
fitX1Click =        False
fitX2Click =        False



def on_clickFig(event):
    global specClickx, specClicky, cutLeftClick, cutRightClick, \
        normalizeClick, fitX1Click, fitX2Click, fitRangeX1, fitRangeX2
    if event.inaxes is not None:
        specClicked = True
        specClickx = event.xdata
        specClicky = event.ydata
    if cutLeftClick:
        cutLeftClick = False
        spec.data = spec.cut(spec.data, specClickx, 'l')
        doPlotFile(spec.data)
        memo_str.set('Data cutted')
    if cutRightClick:
        cutRightClick = False
        spec.data = spec.cut(spec.data, specClickx, 'r')
        doPlotFile(spec.data)
        memo_str.set('Data cutted')
    if normalizeClick:
        normalizeClick = False
        spec.data = spec.normalize(spec.data, specClicky)
        doPlotFile(spec.data)
        memo_str.set('Data normalized')
    if fitX2Click:
        fitRangeX2 = specClickx
        fitX1Click = False
        fitX2Click = False
        doFit(spec.data)
        memo_str.set('Fit done')
    if fitX1Click:
        fitRangeX1 = specClickx
        fitX1Click = False
        fitX2Click = True
        memo_str.set('>> fit:\n Click range right')


canvas.callbacks.connect('button_press_event', on_clickFig)


################################################################################
# Menue

label_separator0 = tk.Label(master=frameMenue, text = '--------  File --------', fg = 'green')
label_separator0.pack(side='top', anchor='w', padx=5, pady = (15,0))


# ComboBox import format
DataFormat = tk.StringVar()
combo_Format = ttk.Combobox(master=frameMenue, width = 16, textvariable = DataFormat)
combo_Format['values'] = ('Spec.dat', 'Spec.txt', 'PicoQuant.dat', 'PicoQuant.phu')
combo_Format.pack(side='top', anchor='w', padx=5, pady = 5)
combo_Format.current(0)


# Load
frameLoad = tk.Frame(frameMenue)
frameLoad.pack(side='top', anchor='w', padx = 5, pady=10)

# Button Load
def btnLoad_callback():
    fTypes = (("All files","*.*"),("all files","*.*"))
    DataTypeNr = combo_Format.current()
    if DataTypeNr == 0:
        fTypes = (("Spec data files","*.dat"),("all files","*.*"))
    if DataTypeNr == 1:
        fTypes = (("Spec data files","*.txt"),("all files","*.*"))
    if DataTypeNr == 2:
        fTypes = (("Time data files","*.dat"),("all files","*.*"))
    FileName =  filedialog.askopenfilename(
        title = "Select file", filetypes = fTypes )
    loadSpec(FileName)
    window.title(sTitle+': '+os.path.basename(spec.dataFileName))
button_Load = tk.Button(master=frameLoad, text = "Load", width=10, height=2, command = btnLoad_callback)
button_Load.pack(side='left')


def btnReLoad_callback():
    loadSpec(spec.dataFileName)
    window.title(sTitle+': '+os.path.basename(spec.dataFileName))
button_reLoad = tk.Button(master=frameLoad, text = "Reload", width=4, height=2, command = btnReLoad_callback)
button_reLoad.pack(side='left', padx = 5)


# Checkbutton plot y-axis in log
def chkPlotYlog_callback():
    dataPlot.plotYlog = plotYlog.get()
    doPlotFile(spec.data)

plotYlog= tk.BooleanVar()
Checkbutton_plotYlog = tk.Checkbutton(master=frameMenue, text="y: log", variable=plotYlog, command = chkPlotYlog_callback)
Checkbutton_plotYlog.pack(side='top', anchor='w', padx=5, pady = 0)


# No spikes, adjust stitching
frameAdjust = tk.Frame(frameMenue)
frameAdjust.pack(side='top', anchor='w', padx = 5, pady=10)

# Button removeSpikes
def btnNoSpikes_callback():
    removeSpikes()
button_noSpikes = tk.Button(master=frameAdjust, text = "No spikes", width=7, height=1, command = btnNoSpikes_callback)
button_noSpikes.pack(side='left')

# Button adjust stitching
def btnAdjStitch_callback():
    correctStitching()
button_adjStitch = tk.Button(master=frameAdjust, text = "Stitch adj", width=7, height=1, command = btnAdjStitch_callback)
button_adjStitch.pack(side='left', padx = 5)


# Slider averaging over points
frameAver = tk.Frame(frameMenue)
frameAver.pack(side='top', anchor='w', padx = (5,15))

def setAver(value):
    spec.smoothPts = int(value)
slider_Aver = tk.Scale(master=frameAver, from_=5, to=35, tickinterval=24,
    orient=tk.HORIZONTAL, width = 12, length = 55, command=setAver)
slider_Aver.pack(side='left')
slider_Aver.set(spec.smoothPts)

def btnSetAver_callback():
    data, smoothPts = spec.smooth(spec.data, 1, spec.smoothPts)
    slider_Aver.set(smoothPts)
    spec.data = data
    spec.smoothPts = smoothPts
    doPlotFile(data)

button_setAver = tk.Button(master=frameAver, text = "Smooth", width=7, height=1,
    command = btnSetAver_callback)
button_setAver.pack(side='left', padx = 1)


# Cut x-range
frameCut = tk.Frame(frameMenue)
frameCut.pack(side='top', anchor='w', padx = 5)

# Button cutLeft
def btnCutLeft_callback():
    global cutLeftClick
    cutLeftClick = True
    memo_str.set('>> Click for cut left')
button_cutLeft = tk.Button(master=frameCut, text = "Cut left", width=7, height=1, command = btnCutLeft_callback)
button_cutLeft.pack(side='left')

# Button cutRight
def btnCutRight_callback():
    global cutRightClick
    cutRightClick = True
    memo_str.set('>> Click for cut right')
button_cutRight = tk.Button(master=frameCut, text = "Cut right", width=7, height=1, command = btnCutRight_callback)
button_cutRight.pack(side='left', padx = 5)


# Normalize
frameNormalize = tk.Frame(frameMenue)
frameNormalize.pack(side='top', anchor='w', padx = 5, pady = 10)
label_normalize = tk.Label(master=frameNormalize, text = 'Norm.')
label_normalize.pack(side='left')
def btnNormalizeMax_callback():
    spec.data = spec.normalize(spec.data, 0)
    doPlotFile(spec.data)
button_normalizeMax = tk.Button(master=frameNormalize, text = "max", width=4, height=1, command = btnNormalizeMax_callback)
button_normalizeMax.pack(side='left', anchor='w', padx=2)
def btnNormalizeClick_callback():
    global normalizeClick
    normalizeClick = True       # see: def on_clickFig(event):
button_normalizeClick = tk.Button(master=frameNormalize, text = "click", width=4, height=1, command = btnNormalizeClick_callback)
button_normalizeClick.pack(side='left', anchor='w', padx=2)


# Math
frameMath = tk.Frame(frameMenue)
frameMath.pack(side='top', anchor='w', padx = 5, pady = 0)
label_Math = tk.Label(master=frameMath, text = 'Math')
label_Math.pack(side='left')
def btnMathAdd_callback():
    val = float(mathVal_str.get())
    spec.data = spec.math(spec.data, 1, val)
    doPlotFile(spec.data)
button_mathAdd = tk.Button(master=frameMath, text = "+", width=1, height=1, command = btnMathAdd_callback)
button_mathAdd.pack(side='left', anchor='w', padx=2)
def btnMathMult_callback():
    val = float(mathVal_str.get())
    spec.data = spec.math(spec.data, 2, val)
    doPlotFile(spec.data)
button_mathMult = tk.Button(master=frameMath, text = "x", width=1, height=1, command = btnMathMult_callback)
button_mathMult.pack(side='left', anchor='w', padx=3)
mathVal_str = tk.StringVar()
entry_mathVal = tk.Entry(master=frameMath, width=6, textvariable=mathVal_str)
entry_mathVal.pack(side='left', anchor='w', padx = (3,0))
mathVal_str.set('1')


# Button nm<>eV
def btnNmeV_callback():
    spec.data = spec.nm2eV(spec.data)
    doPlotFile(spec.data)
button_nmeV = tk.Button(master=frameMenue, text = "nm <-> eV", width=16, height=1, command = btnNmeV_callback)
button_nmeV.pack(side='top', anchor='w', padx=5, pady=5)


# ComboBox fit function
fitFunction = tk.StringVar()
combo_FitFuncion = ttk.Combobox(master=frameMenue, width = 16, textvariable = fitFunction)
#combo_FitFuncion['values'] = ('exp.decay1', 'exp.decay2')
combo_FitFuncion['values'] = fit.peakFitFuncNames()
combo_FitFuncion.pack(side='top', anchor='w', padx=5, pady=5)
combo_FitFuncion.current(0)


# fitting
def doFit(data):
    SpecScale = np.array(data)[ : , 0]
    SpecVals =  np.array(data)[ : , 1]
    funcNr = combo_FitFuncion.current()
    fitResults, fitResultsStr = fit.peakFitting(SpecScale, SpecVals, fitRangeX1, fitRangeX2, funcNr )
    plot.plot(fit.fitXvals, fit.fitYvals)
    canvas.draw()
    fit.fitResultsList.append('\n'+fitResultsStr)
    fit.viewFitResultsList(window)


# Button fit
def btnfit_callback():
    global fitX1Click
    fitX1Click = True
    memo_str.set('>> fit:\n Click range left')

button_fit = tk.Button(master=frameMenue, text="Fit", width=16, command = btnfit_callback)
button_fit.pack(side='top', anchor='w', padx=5)


# Button Save
def btnSave_callback():
    FileName = os.path.basename(os.path.splitext(spec.dataFileName)[0])+'_mod.dat'
    SaveFileName = tk.filedialog.asksaveasfilename(
        defaultextension='.dat', filetypes=[("data files", '*.dat')], title="Save filename", initialfile=FileName)
    saveSpec(SaveFileName)
button_Save = tk.Button(master=frameMenue, text = "Save", width=16, height=1, command = btnSave_callback)
button_Save.pack(side='top', anchor='w', padx=5, pady=10)


label_separator1 = tk.Label(master=frameMenue, text = '------- Plot --------', fg = 'green')
label_separator1.pack(side='top', anchor='w', padx=5, pady = (10,0))


# Button Add to plot
def btnAddToPlot_callback():
    dataPlot.addToPlot(spec.dataFileName, spec.data, 1)
    dataPlot.plotAxisLabels = spec.dataAxisLabels
button_addToPlot = tk.Button(master=frameMenue, text = "Add to plot", width=16, height=1, command = btnAddToPlot_callback)
button_addToPlot.pack(side='top', anchor='w', padx=5, pady=5)


# Select plot
frame_Plot = tk.Frame(frameMenue)
frame_Plot.pack(side='top', anchor='w', padx = 5)
label_Plot = tk.Label(master=frame_Plot, text = 'Show')
label_Plot.pack(side='left')
def btnPlotFile_callback():
    doPlotFile(spec.data)
button_plotFile = tk.Button(master=frame_Plot, text = "File", width=4, height=1, command = btnPlotFile_callback)
button_plotFile.pack(side='left', anchor='w', padx=1)
def btnPlotAll_callback():
    doPlotPlot(dataPlot.plotData)
button_plotAll = tk.Button(master=frame_Plot, text = "Plot", width=5, height=1, command = btnPlotAll_callback)
button_plotAll.pack(side='left', anchor='w', padx=2)


# Button Labels
def btnLabels_callback():
    dataPlot.editPlotLabels(window, plot, fig, canvas)
button_labels = tk.Button(master=frameMenue, text = "Edit plot", width=16, height=1, command = btnLabels_callback)
button_labels.pack(side='top', anchor='w', padx=5, pady=5)


# Button Clear plot
def btnClearPlot_callback():
    dataPlot.plotData = []
    dataPlot.plotDataParameters = []
    dataPlot.plotDataLabels = []
    doPlotFile(spec.data)
button_clearPlot = tk.Button(master=frameMenue, text = "Clear plot", width=16, height=1, command = btnClearPlot_callback)
button_clearPlot.pack(side='top', anchor='w', padx=5, pady=5)


label_separator2 = tk.Label(master=frameMenue, text = '------- Quit --------', fg = 'green')
label_separator2.pack(side='top', anchor='w', padx=5, pady=10)


# Button Quit
def btnQuit_callback():
    window.quit()
    window.destroy()
button_Quit = tk.Button(master=frameMenue, text = "Quit", width=16, command = btnQuit_callback)
button_Quit.pack(side='top', anchor='w', padx=5, pady=1)


# Label Memo
memo_str = tk.StringVar()
label_memo = tk.Label(master=frameMenue, textvariable=memo_str)
label_memo.pack(side='top', pady=5)
memo_str.set('>> Load File')


################################################################################
# Functions

def doPlotFile(data):
    SpecScale = np.array(data)[ : , 0]
    SpecVals =  np.array(data)[ : , 1]
    plot.clear()
    plot.plot(SpecScale, SpecVals, linewidth=0.5, color='black')
    if dataPlot.plotYlog:
        plot.set_yscale('log')
    plot.set_xlabel(spec.dataAxisLabels[0], fontsize=28)
    plot.set_ylabel(spec.dataAxisLabels[1], fontsize=28)
    plot.tick_params(axis='both', which='major', labelsize=20)
    fig.tight_layout()
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)


def doPlotPlot(plotData):
    dataPlot.doPlot(plotData, plot, fig, canvas)


def removeSpikes():
    spec.data = spec.removeSpikes(spec.data, 1)
    doPlotFile(spec.data)


def correctStitching():
    if len(spec.stitchPixel)>0:
        spec.data = spec.correctStitching(spec.data, spec.stitchPixel)
        doPlotFile(spec.data)


def loadSpec(FileName):
    spec.data = spec.importDataFile(FileName)
    doPlotFile(spec.data)
    spec.smoothPts = 5
    slider_Aver.set(spec.smoothPts)


def saveSpec(SaveFileName):
    spec.saveDataFile(spec.data,SaveFileName)


window.mainloop()
