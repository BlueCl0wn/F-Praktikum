#
# Plot handling for spectrometer data
# 05.02.2023
#


import tkinter as tk
from tkinter import ttk
import numpy as np


# Data for plotting
plotData = []
plotDataParameters = []     # fileName, label, Linewidth, lineColor
plotAxisLabels = ['x-axis', 'y-axis']
plotDataLabelPosition = 1
plotYlog = False
colorList = ('k','r','b','g','c','m','y') # 'b'=blue, 'g'=green, 'r'=red, 'c'=cyan, 'm' =magenta, 'y'=yellow, 'k'=black, 'w'=white



def addToPlot(fileName, data, columnNum):
    global plotData, plotDataParameters
    SpecScale = np.array(data)[ : , 0]
    SpecVals =  np.array(data)[ : , columnNum]
    plotData.append([SpecScale, SpecVals])
    label = 'Label '+str(len(plotData))
    lineWidth = 0.5
    colorNum = len(plotData)-1
    if colorNum > 6:
        colorNum = colorNum-6
    lineColor = colorList[colorNum]
    plotDataPara = [fileName, label, lineWidth, lineColor]
    plotDataParameters.append(plotDataPara)

def deleteFromPlot(lineNum):
    if lineNum<=len(plotData):
        plotData.pop(lineNum)
        plotDataParameters.pop(lineNum)
        for i in range(len(plotDataParameters)):
            colorNum = i
            if colorNum > 6:
                colorNum = colorNum-6
            iColor = colorList[colorNum]
            plotDataParameters[i][3] = iColor

def editPlotLabels(window, plot, fig, canvas):
    windowLabels = tk.Toplevel(window)
    windowLabels.geometry('300x400+155+78') # width x heigth + left + top
    windowLabels.title('Edit plot')
    frameLabels = tk.Frame(windowLabels)
    frameLabels.pack()

    xaxis_str = tk.StringVar(); xaxis_str.set(plotAxisLabels[0]);
    frameAxis = tk.Frame(frameLabels); frameAxis.pack(side='top', anchor='w', pady = (5,0))
    label_xaxis = tk.Label(master=frameAxis, width=14, text = 'x-axis text')
    label_xaxis.pack(side='left', anchor='w')
    entry_xaxis = tk.Entry(master=frameAxis, width=20, textvariable=xaxis_str)
    entry_xaxis.pack(side='left', anchor='w', padx = (2,0))
    yaxis_str = tk.StringVar(); yaxis_str.set(plotAxisLabels[1]);
    frameAxis = tk.Frame(frameLabels); frameAxis.pack(side='top', anchor='w', pady = (5,0))
    label_yaxis = tk.Label(master=frameAxis, width=14, text = 'y-axis text')
    label_yaxis.pack(side='left', anchor='w')
    entry_yaxis = tk.Entry(master=frameAxis, width=20, textvariable=yaxis_str)
    entry_yaxis.pack(side='left', anchor='w', padx = (2,0))

    entryList_label = []
    entryList_width = []
    for i in range(len(plotDataParameters)):
        label_str = tk.StringVar()
        width_str = tk.StringVar()
        frame = tk.Frame(frameLabels)
        frame.pack(side='top', anchor='w', pady = (5,0))
        name = 'line'+str(i+1)+' (label, width)';
        label_str.set(plotDataParameters[i][1])
        width_str.set(str(plotDataParameters[i][2]))
        framePara = tk.Frame(frame)
        framePara.pack(side='top', anchor='w', pady = (5,0))
        label_name = tk.Label(master=framePara, width=14, text = name)
        label_name.pack(side='left', anchor='w')
        entry_label = tk.Entry(master=framePara, width=14, textvariable=label_str)
        entry_label.pack(side='left', anchor='w', padx = (2,0))
        entry_width = tk.Entry(master=framePara, width=5, textvariable=width_str)
        entry_width.pack(side='left', anchor='w', padx = (2,0))
        entryList_label.append(label_str)
        entryList_width.append(width_str)

    framePosition = tk.Frame(frameLabels)
    framePosition.pack(side='top', anchor='w', pady = (5,0))
    label_Position = tk.Label(master=framePosition, width=14, text = 'Label position')
    label_Position.pack(side='left')
    combo_Position = ttk.Combobox(master=framePosition, width = 6)
    combo_Position.pack(side='left', anchor='w', padx = 3)
    combo_Position['values'] = ('no','best','left','right')
    combo_Position.current(plotDataLabelPosition )

    def refreshPlot():
        global plotAxisLabels, plotDataParameters, plotDataLabelPosition
        plotAxisLabels[0] = xaxis_str.get()
        plotAxisLabels[1] = yaxis_str.get()
        for i in range(len(plotDataParameters)):
            plotDataParameters[i][1] = entryList_label[i].get()
            plotDataParameters[i][2] = float(entryList_width[i].get())
        plotDataLabelPosition = combo_Position.current()
        windowLabels.destroy()
        doPlot(plotData, plot, fig, canvas)

    frameDelete = tk.Frame(frameLabels)
    frameDelete.pack(side='top', anchor='w', padx = (5,0), pady = (10,0))
    def btnDelete_callback():
        lineNum = combo_Delete.current()
        if lineNum>0:
            deleteFromPlot(lineNum-1)
            refreshPlot()
    button_delete = tk.Button(master=frameDelete, text = "Delete", width=8, height=1, command = btnDelete_callback)
    button_delete.pack(side='left', anchor='w', padx = 10)
    combo_Delete = ttk.Combobox(master=frameDelete, width = 17)
    combo_Delete.pack(side='left', anchor='w', padx = 15)
    lineLabels = ['- none -']
    for i in range(len(plotDataParameters)):
        lineLabels.append(plotDataParameters[i][1])
    combo_Delete['values'] = lineLabels
    combo_Delete.current(0)

    frameButtons = tk.Frame(frameLabels)
    frameButtons.pack(side='top', anchor='w', padx = (5,0), pady = (10,0))
    def btnAccept_callback():
        refreshPlot()
    button_accept = tk.Button(master=frameButtons, text = "Accept", width=8, height=1, command = btnAccept_callback)
    button_accept.pack(side='left', anchor='w', padx=10)
    def btnQuit_callback():
        windowLabels.destroy()
    button_quit = tk.Button(master=frameButtons, text = "Quit", width=8, height=1, command = btnQuit_callback)
    button_quit.pack(side='left', anchor='w', padx=15)


def doPlot(plotData, plot, fig, canvas):
    plot.clear()
    colorList = ('k','r','b','g','c','m','y') # 'b'=blue, 'g'=green, 'r'=red, 'c'=cyan, 'm' =magenta, 'y'=yellow, 'k'=black, 'w'=white
    labels = []
    for i in range(len(plotData)):
        SpecScale = plotData[i][0]
        SpecVals =  plotData[i][1]
        iLabel = plotDataParameters[i][1]
        iWidth = plotDataParameters[i][2]
        iColor = plotDataParameters[i][3]
        labels.append(iLabel)
        plot.plot1(SpecScale, SpecVals, linewidth=iWidth, color=iColor)
    plot.set_xlabel(plotAxisLabels[0], fontsize=28)
    plot.set_ylabel(plotAxisLabels[1], fontsize=28)
    plot.tick_params(axis='both', which='major', labelsize=20)
    if len(plotData) > 1:
        if plotDataLabelPosition == 1:
            plot.legend(labels, fontsize=20, loc="best")
        if plotDataLabelPosition == 2:
            plot.legend(labels, fontsize=20, loc="upper left")
        if plotDataLabelPosition == 3:
            plot.legend(labels, fontsize=20, loc="upper right")
    fig.tight_layout()
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)


