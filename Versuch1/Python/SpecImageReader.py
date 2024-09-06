# ******************************
# *
# *  Viewer for spectrometer images
# *
# ******************************
# Gui

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import utils.data_Fit as fit
import utils.data_Image as dataImage

sTitle = 'Viewer for spectrometer images (V07.02.2024)'

colMap = 'gray'

brigthLow =  0
brigthHigh = 255

# Main window
window = tk.Tk()
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
window.title(sTitle)
window_width = screenwidth-20; window_height = screenheight-100;
window.geometry( str(window_width)+'x'+str(window_height)+'+5+5')             # Window size

# Frames
frameMenue = tk.Frame(window)
frameFig1 = tk.Frame(window)
frameFig2 = tk.Frame(window)

# Figures
#fig1 = Figure()
fig1 = Figure(figsize=(12,3))
plot1 = fig1.add_subplot(111)
fig2 = Figure(figsize=(12,3))
#fig2 = Figure()
plot2 = fig2.add_subplot(111)

# Canvas
canvas1 = FigureCanvasTkAgg(fig1, window)
toolbar1 = NavigationToolbar2Tk(canvas1, frameFig1)
canvas2 = FigureCanvasTkAgg(fig2, window)
toolbar2 = NavigationToolbar2Tk(canvas2, frameFig2)

# pack() geometry manager
frameMenue.pack(side='left', anchor='n', padx=10)
frameFig1.pack(side='top',  anchor='w')
canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.X)
frameFig2.pack(side='top',  anchor='w', pady=10)
canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.X)


# PLot image
def ShowImage():
    fig1.clf()
    rangeX1 = dataImage.SpecScale[0]; rangeX2 = dataImage.SpecScale[dataImage.xPixel-2]
    xyAspect = (rangeX2-rangeX1)/dataImage.xPixel
    fig1.add_subplot(111).imshow(dataImage.SpecImage, extent=[rangeX1, rangeX2, 1, dataImage.yPixel],
        aspect=xyAspect, origin='lower', cmap=colMap, vmin=brigthLow, vmax=brigthHigh)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.X)


# PLot spectrum
def ShowSpec():
    fig2.clf()
    SpecScale, SpecVals = dataImage.CreateSpec(dataImage.SpecImage, dataImage.lineNr)
    if dataImage.Spec2Type == 0:
        if fit.isFitted: fig2.add_subplot(111).plot(SpecScale, SpecVals, fit.fitXvals, fit.fitYvals, linewidth=0.5)
        else: fig2.add_subplot(111).plot(SpecScale, SpecVals, linewidth=0.5, color='black')
    else:
        fig2.add_subplot(211).plot(SpecScale, SpecVals)
        if dataImage.Spec2Type == 1: x, y = dataImage.CalcRange()
        if dataImage.Spec2Type == 2: x, y = dataImage.CalcDerivative()
        fig2.add_subplot(212).plot(x, y)
    canvas2.draw()
    canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.X)
    fit.isFitted = False


# Label Image
label_Image = tk.Label(master=frameMenue, text = '<< Image >>')
label_Image.pack(side='top', anchor='sw', pady = (10,0))


# ComboBox import format
SpecFormat = tk.StringVar()
combo_Format = ttk.Combobox(master=frameMenue, width = 12, textvariable = SpecFormat)
combo_Format['values'] = ('Andor.sif', 'Andor.asc', 'NumPy.npy')
combo_Format.pack(side='top', pady = 5)
combo_Format.current(dataImage.fileType)


# Button Load
def btnLoad_callback():
    global brigthLow, brigthHigh
    dataImage.fileType = combo_Format.current()
    if dataImage.fileType == 0:
        dataImage.FileName =  filedialog.askopenfilename(title = "Select file",
                                                    filetypes = (("Andor-SIF files","*.sif"),("all files","*.*")))
    if dataImage.fileType == 1:
        dataImage.FileName =  filedialog.askopenfilename(title = "Select file",
                                                    filetypes = (("Andor-ASCII files","*.asc"),("all files","*.*")))
    if dataImage.fileType == 2:
        dataImage.FileName =  filedialog.askopenfilename(title = "Select file",
                                                    filetypes = (("NumPy files","*.npy"),("all files","*.*")))
    dataImage.LoadFile(dataImage.FileName)
    dataImage.lineNr = dataImage.DetectLineMaxVal(dataImage.Background)
    dataImage.CreateSpec(dataImage.SpecImage, dataImage.lineNr)
    dataImage.SpecImage_bak = dataImage.SpecImage.copy()
    brigthLow=dataImage.CalcDark(); brigthLow_str.set(str(int(brigthLow)))
    brigthHigh=dataImage.SpecImage.max(); brigthHigh_str.set(str(int(brigthHigh)))
    window.title(sTitle+': '+dataImage.FileName)
    label_Format['text'] = str(dataImage.xPixel)+' x '+str(dataImage.yPixel)+' px'
    label_LineNr['text'] =  'y-Line: '+str(dataImage.lineNr+1)
    memo_str.set('-- Log --')
    ShowImage(); fig2.clf(); ShowSpec()

button_Load = tk.Button(master=frameMenue, text = "Load", width=12, command = btnLoad_callback)
button_Load.pack(side='top')


# Brighness
frameBrighness = tk.Frame(frameMenue)
frameBrighness.pack(side='top', anchor='w', pady=(5,0))
label_Bright = tk.Label(master=frameBrighness, text = 'Brighness')
label_Bright.pack(side='top', anchor='w', padx = (10,0))
frameBrighnessEntry = tk.Frame(frameBrighness)
frameBrighnessEntry.pack(side='top', anchor='w')
brigthLow_str = tk.StringVar()
entry_brigthLow = tk.Entry(master=frameBrighnessEntry, width=5, textvariable=brigthLow_str)
entry_brigthLow.pack(side='left', padx = (30,0))
brigthLow_str.set('0')
brigthHigh_str = tk.StringVar()
entry_brigthHigh = tk.Entry(master=frameBrighnessEntry, width=5, textvariable=brigthHigh_str)
entry_brigthHigh.pack(side='left', padx = (5,0))
brigthHigh_str.set('255')
frameBrighnessButton = tk.Frame(frameBrighness)
frameBrighnessButton.pack(side='top', anchor='w')
def button_BrightOK_callback():
    global brigthLow, brigthHigh
    brigthLow = int(brigthLow_str.get())
    brigthHigh = int(brigthHigh_str.get())
    ShowImage()
button_BrightOK = tk.Button(master=frameBrighnessButton, text = "Apply", width=5, command = button_BrightOK_callback)
button_BrightOK.pack(side='left', padx = (30,0))
def button_BrightAuto_callback():
    global brigthLow, brigthHigh
    brigthLow=dataImage.SpecImage.min(); brigthLow_str.set(str(int(brigthLow)))
    brigthHigh=dataImage.SpecImage.max(); brigthHigh_str.set(str(int(brigthHigh)))
    ShowImage(); fig2.clf(); ShowSpec()
button_BrightAuto = tk.Button(master=frameBrighnessButton, text = "Auto", width=4, command = button_BrightAuto_callback)
button_BrightAuto.pack(side='left', padx = (5,0))

# Button no spikes
def btnNoSpikes_callback():
    dataImage.RemoveSpikes(dataImage.SpecImage)
    label_LineNr['text'] =  'y-Line: '+str(dataImage.lineNr+1)
    button_BrightAuto_callback()
    fig2.clf(); ShowSpec()
button_noSpikes = tk.Button(master=frameBrighness, text = "No spikes", width=8, command = btnNoSpikes_callback)
button_noSpikes.pack(side='top', padx = (10,0), pady = (5,5))

# Tilting
frameTilt = tk.Frame(frameMenue)
frameTilt.pack(side='top', anchor='w', pady=(5,0))
label_Tilt = tk.Label(master=frameTilt, text = 'Tilting')
label_Tilt.pack(side='top', anchor='w', padx = (10,0))
frameTiltEntry = tk.Frame(frameTilt)
frameTiltEntry.pack(side='top', anchor='w')
tilt_str = tk.StringVar()
entry_tilt = tk.Entry(master=frameTiltEntry, width=5, textvariable=tilt_str)
entry_tilt.pack(side='left', padx = (30,0))
tilt_str.set('0')
def button_Tilt_callback():
    tiltPixel = int(tilt_str.get())
    dataImage.doTilting(tiltPixel)
    ShowImage()
    fig2.clf(); ShowSpec()
button_Tilt = tk.Button(master=frameTilt, text = "Apply", width=5, command = button_Tilt_callback)
button_Tilt.pack(side='left', padx = (30,0))


# Checkbutton remove dark
def chkRemDark_callback():
    dataImage.SwitchRemoveDark = remDark.get()
    fig2.clf(); ShowSpec()

remDark = tk.BooleanVar()
Checkbutton_RemDark = tk.Checkbutton(master=frameMenue, text="Remove dark", variable=remDark, command = chkRemDark_callback)
Checkbutton_RemDark.pack(side='top', pady=(5,5))
if dataImage.SwitchRemoveDark: remDark.set(True)


# Label camera size
label_Format = tk.Label(master=frameMenue, text = '--')
label_Format.pack(side='top', anchor='sw', padx = (10,0))


# Buttons line up, down
def refrSpec():
    if dataImage.lineNr > dataImage.yPixel-1: dataImage.lineNr = dataImage.yPixel-1
    if dataImage.lineNr < 0: dataImage.lineNr = 0
    label_LineNr['text'] = 'y-Line: '+str(dataImage.lineNr+1)
    fig2.clf(); ShowSpec()

def btnLineUp_callback():
    dataImage.lineNr = dataImage.lineNr+1; refrSpec()
def btnLineDown_callback():
    dataImage.lineNr = dataImage.lineNr-1; refrSpec()

label_LineNr = tk.Label(master=frameMenue, text = 'y-Line: '+str(dataImage.lineNr+1))
label_LineNr.pack(side='top', anchor='sw', padx = (10,0))

frameLineUpDown = tk.Frame(frameMenue)
frameLineUpDown.pack(side='top')
button_LineUp =   tk.Button(master=frameLineUpDown, text = "+", width=5, command = btnLineUp_callback)
button_LineUp.pack(side='left')
button_LineDown = tk.Button(master=frameLineUpDown, text = "-", width=5, command = btnLineDown_callback)
button_LineDown.pack(side='left')


# averaging over points along y
frameAver = tk.Frame(frameMenue)
frameAver.pack(side='top', anchor='w', padx = (5,15))

label_Aver = tk.Label(master=frameAver, text = 'Ave.y')
label_Aver.pack(side='left')

def setAver(value):
    dataImage.avePtsY = int(value)
    if dataImage.avePtsY % 2 == 0:
        dataImage.avePtsY = dataImage.avePtsY+1
        slider_Aver.set(dataImage.avePtsY)
    ShowSpec()
slider_Aver = tk.Scale(master=frameAver, from_=1, to=19,
    orient=tk.HORIZONTAL, width = 15, length = 55, command=setAver)
slider_Aver.pack(side='left', padx = 5)
slider_Aver.set(dataImage.avePtsY)


# Label Spectrum
label_Spectrum = tk.Label(master=frameMenue, text = '<< Spectrum >>')
label_Spectrum.pack(side='top', anchor='sw', pady = (10,0))


# Checkbutton x-axis in eV
def chkShowXeV_callback():
    dataImage.SpecUnits = 0
    if showXeV.get(): dataImage.SpecUnits = 1
    fig2.clf(); ShowSpec()

showXeV = tk.BooleanVar()
Checkbutton_showXeV = tk.Checkbutton(master=frameMenue, text="nm->eV", variable=showXeV, command = chkShowXeV_callback)
Checkbutton_showXeV.pack(side='top', anchor='w', pady = 5)


# Button integrate
def btnIntegrate_callback():
    integrVal = dataImage.Integrate()
    print(integrVal)
button_integrate = tk.Button(master=frameMenue, text="Integrate", width=12, command = btnIntegrate_callback)
#button_integrate.pack(side='top', pady = (10,0))


# ComboBox fit function
fitFunction = tk.StringVar()
combo_FitFuncion = ttk.Combobox(master=frameMenue, width = 16, textvariable = fitFunction)
combo_FitFuncion['values'] = ('lorentzian', 'gaussian', 'lorentzian+backgr.', 'gaussian+backgr.')
combo_FitFuncion.pack(side='top', pady = 5)
combo_FitFuncion.current(0)


# fitting
fitActive = False
fitX1_OK = False

def doFit():
    SpecScale, SpecVals = dataImage.CreateSpec(dataImage.SpecImage, dataImage.lineNr)
    funcNr = combo_FitFuncion.current()
    fitResults, fitResultsStr = fit.peakFitting(SpecScale, SpecVals, fit.fitRangex1, fit.fitRangex2, funcNr )
    fit.isFitted = True
    ShowSpec()
    s = '>'+fit.fitFunctionID[funcNr][0]+' fit'
    for i in range(1, len(fit.fitFunctionID[funcNr])):
        s=s+'\n'+fit.fitFunctionID[funcNr][i]+': {0: >#5.6f}'.format(abs(fitResults[i-1]))
    memo_str.set(s)
    s = ''
    for i in range(1, len(fit.fitFunctionID[funcNr])):
        s=s+'{0: >#5.6f}'.format(abs(fitResults[i-1]))+'  '
    fit.fitResultsList.append('\n'+fitResultsStr)


# Button fit
def btnfit_callback():
    global fitActive
    fitActive = True
    funcNr = combo_FitFuncion.current()
    s = '>'+fit.fitFunctionID[funcNr][0]+' fit\n Click range left'
    memo_str.set(s)

button_fit = tk.Button(master=frameMenue, text="Fit", width=12, command = btnfit_callback)
button_fit.pack(side='top')


def btnShowList_callback():
    funcNr = combo_FitFuncion.current()
    fit.viewFitResultsList(window)

button_showList = tk.Button(master=frameMenue, text="Show list", width=12, command = btnShowList_callback)
button_showList.pack(side='top')


# Checkbutton diff
def chkShowDiff_callback():
    dataImage.Spec2Type = 0
    if showDiff.get():
        dataImage.Spec2Type = 2
    fig2.clf(); ShowSpec()

showDiff = tk.BooleanVar()
Checkbutton_showDiff = tk.Checkbutton(master=frameMenue, text="Derivative2", variable=showDiff, command = chkShowDiff_callback)
#Checkbutton_showDiff.pack(side='top', anchor='w', pady = (10,0))


# Button Save
def btnSave_callback():
    SpecScale, SpecVals = dataImage.CreateSpec(dataImage.SpecImage, dataImage.lineNr)
    SpecSave = []
    for ix in range(0, len(SpecVals)):
        SpecSave.append([str(SpecScale[ix])+'  '+str(SpecVals[ix]) ])
    if dataImage.avePtsY == 1:
        SaveFileName =  dataImage.FileName+'_Line'+str(dataImage.lineNr+1)+'.dat'
    else:
        SaveFileName =  dataImage.FileName+'_Line'+str(dataImage.lineNr+1)+'R'+str(dataImage.avePtsY)+'.dat'
    separatorChar = '\t'
    headerStr = 'x-label = Wavelength [nm]'+'\n'+'y-label = Counts'
    np.savetxt(SaveFileName, SpecSave, delimiter=separatorChar, header=headerStr, fmt='%s')


button_Save = tk.Button(master=frameMenue, text = "Save", width=12, command = btnSave_callback)
button_Save.pack(side='top', pady = (15,0))


# Button Quit
def _quit():
    window.quit()
    window.destroy()

button_Quit = tk.Button(master=frameMenue, text='Quit', width=12, command=_quit)
button_Quit.pack(side='top', pady = (15,0))


# Label Memo
memo_str = tk.StringVar()
label_memo = tk.Label(master=frameMenue, textvariable=memo_str)
label_memo.pack(side='top', pady = (10,0))
memo_str.set('-- Log --')


# Mouse click into camera image
def on_clickFig1(event):
    if event.inaxes is not None:
        dataImage.lineNr = int(event.ydata); refrSpec()
canvas1.callbacks.connect('button_press_event', on_clickFig1)


# Mouse click into spectrum
def on_clickFig2(event):
    global SpecClick, fitActive, fitX1_OK
    if event.inaxes is not None:
        dataImage.SpecClickx = event.xdata
        if fitActive:
            if fitX1_OK == False:
                fitX1_OK = True
                fit.fitRangex1 = dataImage.SpecClickx
                funcNr = combo_FitFuncion.current()
                s = '>'+fit.fitFunctionID[funcNr][0]+' fit'
                if dataImage.SpecUnits == 0:
                    s = s+'\n Left: '+str(round(dataImage.SpecClickx,1))
                if dataImage.SpecUnits == 1:
                    s = s+'\n Left: '+str(round(dataImage.SpecClickx,3))
                s = s+'\n Click range right'
                memo_str.set(s)
            else:
                fitActive = False
                fitX1_OK = False
                fit.fitRangex2 = dataImage.SpecClickx
                doFit()

        if dataImage.SpecUnits == 0:
            s = str(round(dataImage.SpecClickx,1))
        if dataImage.SpecUnits == 1:
            s = str(round(dataImage.SpecClickx,3))
        #button_fit.config(text='fit '+s)
        #label_Clicked['text'] = 'Clicked x='+s

canvas2.callbacks.connect('button_press_event', on_clickFig2)

window.mainloop()