# https://github.com/emilyripka/BlogRepo/blob/master/181119_PeakFitting.ipynb
# http://www.emilygraceripka.com/blog/16
# https://towardsdatascience.com/basic-curve-fitting-of-scientific-data-with-python-9592244a2509
# https://www.diffpy.org/diffpy.srmise/tutorial/fit_initial.html
# https://lentner.io/2018/06/14/autogui-for-curve-fitting-in-python.html
# https://www8.physics.utoronto.ca/~phy326/python/curve_fit_to_data.py


import tkinter as tk
from tkinter import scrolledtext
import math
import numpy as np
import scipy as scipy
from scipy import optimize
from scipy.optimize import curve_fit
#import utils.SpecImageReader_Import as spec



isFitted = False
fitXvals = []; fitYvals = []
viewFitWindowIsOpen = False

fitFunctionID = [['lorentzian',     'y0', 'xc', 'w', 'A'],
                 ['gaussian',       'y0', 'xc', 'w', 'A'],
                 ['lorentzian+bg',  'y0', 'xc', 'w', 'A', 'dy'],
                 ['gaussian+bg',    'y0', 'xc', 'w', 'A', 'dy'] ]

fitRangex1 = 0
fitRangex2 = 0
fitResults = ''
fitResultsList = []

################################################################################
# Peak fitting


def peakFitFuncNames():
    names = ['lorentzian','gaussian','lorentzian+bg','gaussian+bg']
    return names

def peakFitParaStr(funcNr):
    s = ''
    if funcNr == 0:
        s = 'y0,xc,w,A'
    if funcNr == 1:
        s = 'y0,xc,w,A'
    if funcNr == 2:
        s = 'y0,xc,w,A,dy'
    if funcNr == 3:
        s = 'y0,xc,w,A,dy'
    return s

def lorentzian(x, y0, xc, w, A):
# y = y0 + (2*A/pi)*(w/(4*(x-xc)^2 + w^2))
    return y0 + (2*A/np.pi)*(w/(4*(x-xc)**2 + w**2))

def gaussian(x, y0, xc, w, A):
    # y=y0 + (A/(w*sqrt(pi/2)))*exp(-2*((x-xc)/w)^2)
        return y0 + (A/(w*np.sqrt(np.pi/2)))*np.exp(-2*((x-xc)/w)**2)

def lorentzian_bg(x, y0, xc, w, A, dy):
# y=y0+dy*x + (2*A/pi)*(w/(4*(x-xc)^2 + w^2))
    bg = y0+np.multiply(x, dy)      # linear background
    return bg + (2*A/np.pi)*(w/(4*(x-xc)**2 + w**2))

def gaussian_bg(x, y0, xc, w, A, dy):
# y=y0+dy*x + (A/(w*sqrt(pi/2)))*exp(-2*((x-xc)/w)^2)
    bg = y0+np.multiply(x, dy)      # linear background
    return bg + (A/(w*np.sqrt(np.pi/2)))*np.exp(-2*((x-xc)/w)**2)

# funcNr 0: lorentzian
# funcNr 1: gaussian
# funcNr 2: lorentzian with background
# funcNr 3: gaussian with background
def peakFitting(Xvals, Yvals, rangeX1, rangeX2, funcNr):
    global fitXvals, fitYvals
    XvalsCut = []; YvalsCut = []
    for i in range(len(Xvals)):
        if (Xvals[i] >= rangeX1) and (Xvals[i] <= rangeX2):
            XvalsCut.append(Xvals[i])
            YvalsCut.append(Yvals[i])
    #y0 = min(YvalsCut)
    y0 = YvalsCut[0]
    xc = (max(XvalsCut)+min(XvalsCut))/2
    w =  (max(XvalsCut)-min(XvalsCut))/2
    A = w/4*max(YvalsCut)
    dy = YvalsCut[len(YvalsCut)-1]-y0
    fitXvals = XvalsCut; fitYvals = []
    if funcNr == 0:
        popt, pcov = curve_fit(lorentzian, XvalsCut, YvalsCut, p0=[y0, xc, w, A])
        for i in range(len(fitXvals)):
            fitYvals.append(lorentzian(fitXvals[i], popt[0], popt[1], popt[2], popt[3]))
    if funcNr == 1:
        popt, pcov = curve_fit(gaussian, XvalsCut, YvalsCut, p0=[y0, xc, w, A])
        for i in range(len(fitXvals)):
            fitYvals.append(gaussian(fitXvals[i], popt[0], popt[1], popt[2], popt[3]))
    if funcNr == 2:
        popt, pcov = curve_fit(lorentzian_bg, XvalsCut, YvalsCut, p0=[y0, xc, w, A, dy])
        for i in range(len(fitXvals)):
            fitYvals.append(lorentzian_bg(fitXvals[i], popt[0], popt[1], popt[2], popt[3], popt[4]))
    if funcNr == 3:
        popt, pcov = curve_fit(gaussian_bg, XvalsCut, YvalsCut, p0=[y0, xc, w, A, dy])
        for i in range(len(fitXvals)):
            fitYvals.append(gaussian_bg(fitXvals[i], popt[0], popt[1], popt[2], popt[3], popt[4]))
    fitResults = popt
    fitResultsStr = peakFitParaStr(funcNr)+'\t'
    for i in range(len(fitResults)):
        fitResultsStr = fitResultsStr + str(fitResults[i])+'\t'
    return fitResults, fitResultsStr



################################################################################
# Exponential fitting

def expFitFuncNames():
    names = ['exp.decay1', 'exp.decay2']
    return names

def expFitParaStr(funcNr):
    s = ''
    if funcNr == 0:
        s = 'y0,A1,t1'
    if funcNr == 1:
        s = 'y0,A1,t1,A2,t2'
    return s


def exp_decay1(x, y0, A1, t1):
    return y0 + A1*np.exp(-x/t1)

def exp_decay2(x, y0, A1, t1, A2, t2):
    return y0 + A1*np.exp(-x/t1) + A2*np.exp(-x/t2)

# funcNr 0: exp decay 1
# funcNr 1: exp decay 2
def expFitting(Xvals, Yvals, rangeX1, rangeX2, funcNr):
    global fitXvals, fitYvals
    XvalsCut = []; YvalsCut = []
    for i in range(len(Xvals)):
        if (Xvals[i] >= rangeX1) and (Xvals[i] <= rangeX2):
            XvalsCut.append(Xvals[i])
            YvalsCut.append(Yvals[i])
    y0 = YvalsCut[len(XvalsCut)-1]
    A1 = 1
    t1 = 1
    A2 = 1
    t2 = 5
    fitXvals = XvalsCut; fitYvals = []
    if funcNr == 0:
        popt, pcov = curve_fit(exp_decay1, XvalsCut, YvalsCut, p0=[y0, A1, t1])
        for i in range(len(fitXvals)):
            fitYvals.append(exp_decay1(fitXvals[i], popt[0], popt[1], popt[2]))
    if funcNr == 1:
        popt, pcov = curve_fit(exp_decay2, XvalsCut, YvalsCut, p0=[y0, A1, t1, A2, t2])
        for i in range(len(fitXvals)):
            fitYvals.append(exp_decay2(fitXvals[i], popt[0], popt[1], popt[2], popt[3], popt[4]))
    fitXvals = XvalsCut
    fitResults = popt
    fitResultsStr = expFitParaStr(funcNr)+'\t'
    for i in range(len(fitResults)):
        fitResultsStr = fitResultsStr + str(fitResults[i])+'\t'
    return fitResults, fitResultsStr


################################################################################
# Show fit results list

def viewFitResultsList(window):
    newWindow = tk.Toplevel(window)
    newWindow.geometry('1100x500+125+40')

    # Edit fit results
    text_area = scrolledtext.ScrolledText(newWindow,
                                          wrap = tk.WORD,
                                          width = 200,
                                          height = 20
                                          )
    #text_area.insert(tk.INSERT, fitResultsList)
    for i in range(len(fitResultsList)):
            text_area.insert(tk.INSERT, fitResultsList[i])
    text_area.pack(side='top', padx = (5,0), pady = (15,0))

    frameButtons = tk.Frame(newWindow)
    frameButtons.pack(side='top', anchor='w', padx = (5,0), pady = (15,0))

    # Button Quit
    def btnQuit_callback():
        global viewFitWindowIsOpen
        newWindow.destroy()
        viewFitWindowIsOpen = False
    button_Quit = tk.Button(master=frameButtons, text = "Quit", width=20,
                            command =  btnQuit_callback)
    button_Quit.pack(side='left')


    # Button Clear
    def btnClear_callback():
        global fitResultsList, viewFitWindowIsOpen
        if viewFitWindowIsOpen:
            return
        fitResultsList = []
        newWindow.destroy()
        viewFitWindowIsOpen = False

    button_Clear = tk.Button(master=frameButtons, text = "Clear list", width=8,
                            command =  btnClear_callback)
    button_Clear.pack(side='left', padx = (500,0))




