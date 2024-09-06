#
# File handling for Viewer for data files
# 08.03.2023
#


import os
import numpy as np
from scipy import signal
import statistics as st


# Loaded data from file
dataFileName = ''
data = []
dataRowsNum = 0
smoothPts = 5
headerChar = '#'
dataAxisLabels = ['x-axis', 'y-axis']
dataHeader = []
stitchPixel = []


def headerLineLoad(line):
    global dataAxisLabels, dataHeader, stitchPixel
    splitLine = line.split('=')
    isDone = False
    if splitLine[0].strip() == 'x-label':   dataAxisLabels[0] = splitLine[1].strip(); isDone = True
    if splitLine[0].strip() == 'y-label':   dataAxisLabels[1] = splitLine[1].strip(); isDone = True
    if splitLine[0].strip() == 'Stitching':
        slitVals = splitLine[1].split(';')
        for i in range(len(slitVals)):
            s = slitVals[i].strip()
            if len(s)>0:
                val = int(s)
                stitchPixel.append(val)
        isDone = True;
    if isDone == False: dataHeader.append(line.strip())


def cut(data, cutPos, leftright):
    global stitchPixel
    cutData = []
    for i in range(len(data)):
        if leftright =='l':
            if data[i][0] > cutPos:
                cutData.append(data[i])
        if leftright =='r':
            if data[i][0] < cutPos:
                cutData.append(data[i])
    stitchPixel = []
    return cutData


def removeSpikes(data, columnNum):
    columnNum = 1
    specValsDiff = np.zeros(len(data))
    sumDiff = 0
    for ix in range(1, len(specValsDiff)-2):
        diff = data[ix][columnNum] - data[ix-1][columnNum]
        sumDiff = sumDiff+abs(diff)
        specValsDiff[ix]=diff
    meanDiff = sumDiff/len(specValsDiff)
    for ix in range(1, len(specValsDiff)-1):
        if specValsDiff[ix]>10*meanDiff:
            data[ix][columnNum] = data[ix-1][columnNum]
    return data


def correctStitching(data, stitchPixel):
# Corrects the left an Right borders by an offset
    avePix = 3
    sPixL = 0
    xVals = np.array(data)[ : , 0]
    # Add offset if average is below zero
    for iSp in range(len(stitchPixel)):
        y = np.array(data)[ : , 1]
        sPixR = stitchPixel[iSp]
        if sPixL > sPixR: sPixL = 0
        if sPixR < len(data):
            yL = st.mean(y[sPixL : sPixL+avePix])
            yR = st.mean(y[sPixR-avePix : sPixR])
            offs = 0
            if yL<offs: offs=yL
            if yR<offs: offs=yR
            if offs<0:
                for jx in range(sPixL, sPixR):
                    x = jx-sPixL
                    data[jx][1] = data[jx][1]-offs
        sPixL = sPixR

    # Add linear function
    sPixL = 0
    for iSp in range(len(stitchPixel)):
        y = np.array(data)[ : , 1]
        sPixR = stitchPixel[iSp]
        if sPixR < len(data):
            yL2 = st.mean(y[sPixL : sPixL+avePix])
            if iSp == 0: yL1 = yL2
            else: yL1 = st.mean(y[sPixL-avePix : sPixL])
            yR1 = st.mean(y[sPixR-avePix : sPixR])
            if iSp == len(stitchPixel): yR2 = yR1
            else: yR2 = st.mean(y[sPixR  : sPixR+avePix])
            offsL = yL1-yL2
            if yR1 < yR2: offsR = (yR2-yR1)
            #if yL2 < yR1: offsR = (yR2-yR1)/2
            #if yL2 > yR1: offsR = (yR2-yR1)/2
            else: offsR = 0
            dx = sPixR-sPixL
            a = offsL
            b =  (offsR-offsL)/dx
            for jx in range(sPixL, sPixR):
                x = jx-sPixL
                offs = a+b*x
                data[jx][1] = data[jx][1]+offs
            sPixL = sPixR
    return data


def normalize(data, divider):
    if divider == 0:
        SpecVals =  np.array(data)[ : , 1]
        divider = np.max(SpecVals)
    for ix in range(len(data)):
        data[ix][1] = data[ix][1]/divider
    return data


def smooth(data, columnNum, smoothPts):
    if smoothPts%2 == 0: smoothPts -= 1
    y = np.array(data)[ : , 1]
    y_smooth = signal.savgol_filter(y, window_length=smoothPts, polyorder=3, mode="nearest")
    for ix in range(len(y)):
        data[ix][columnNum] = y_smooth[ix]
    return data, smoothPts


def math(data,operationNr,val):
    # operationNr=1: addition, 2: multiplication
    for ix in range(len(data)):
        if operationNr == 1:
            data[ix][1] = data[ix][1]+val
        if operationNr == 2:
            data[ix][1] = data[ix][1]*val
    return data


def nm2eV(data):
    global dataAxisLabels
    for ix in range(len(data)):
        data[ix][0] = 1240/data[ix][0]
    SpecScale = np.array(data)[ : , 0]
    if max(SpecScale) > 100:
        dataAxisLabels[0] = 'Wavelength [nm]'
    else:
        dataAxisLabels[0] = 'Energy [eV]'
    return data


def analyzeDataFormat(line):
    allowedNumChars = '0123456789-+.eE'
    OK = True; i = 0
    # first numerial value
    while OK:
        if line[i] in allowedNumChars:
            i += 1
        else: OK = False
    # separator
    OK = True; separatorChar = ''
    while OK:
        if line[i] not in allowedNumChars:
            separatorChar = separatorChar+line[i]; i += 1
        else: OK = False
    return separatorChar


def importDataFile(FileName):
    global dataFileName, data, dataRowsNum, dataAxisLabels, dataHeader, stitchPixel
    dataFileName = FileName
    headerStr = ''
    data = []
    dataHeader = []
    stitchPixel = []
    # read file
    dataLines = []
    with open(FileName) as dataFile:
        lines = dataFile.readlines()
    for line in lines:
        if line[0] == headerChar:
            headerStr = line[1:].strip()
            headerLineLoad(headerStr)
        else:
            if line[0] in '-0123456789.':
                dataLines.append(line.strip())
    # analyze data
    line = dataLines[0]
    separatorChar = analyzeDataFormat(line)
    splitLine = line.split(separatorChar)
    dataRowsNum = len(splitLine)
    for line in dataLines:
        splitLine = line.split(separatorChar)
        dataLine = []
        for dataStr in splitLine:
            dataLine.append(float(dataStr))
        data.append(dataLine)
    return data


def importTimeData(FileName):
    global dataFileName, data, dataRowsNum, dataAxisLabels
    dataFileName = FileName
    headerLinesNum = 0
    dataAxisLabels = ['Time [ns]', 'Counts']
    ns_channel = 0
    data = []
    # read file
    headerLines = []; dataLines = []
    with open(FileName) as dataFile:
        lines = dataFile.readlines()
    i = 0
    for line in lines:
        i += 1
        if line[0:11] == '#ns/channel':
            ns_channel = float(lines[i])
        if line[0:7] == '#counts':
            headerLinesNum = i
    i = 0
    for line in lines:
        i += 1
        if i > headerLinesNum:
            dataLine = [(i-headerLinesNum)*ns_channel]
            dataLine.append(float(line))
            data.append(dataLine)
    # Cut zero values at high times
    done = False; cutX = 1e25
    for i in range(len(data)):
        if not done:
            ix = len(data)-1-i
            #print(ix, data[ix][0], data[ix][1])
            if data[ix][1] != 0:
                done = True
            cutX = data[ix-3][0]
    if done:
        data = cut(data, cutX, 'r')
    return data


def saveDataFile(data, SaveFileName):
    headerStr = ''
    if len(dataHeader) > 0:
        for i in range(len(dataHeader)):
            headerStr = headerStr+dataHeader[i]+'\n'
    headerStr = headerStr+'x-label = '+dataAxisLabels[0]+'\n'
    headerStr = headerStr+'y-label = '+dataAxisLabels[1]
    separatorChar = '\t'        # tab
    np.savetxt(SaveFileName, data, delimiter=separatorChar, header=headerStr, fmt='%s')

