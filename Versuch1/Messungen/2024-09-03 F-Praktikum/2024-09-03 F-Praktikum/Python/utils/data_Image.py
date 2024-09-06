'''

Camera image  handling for viewer for spectrometer data

by Ch. Heyn

'''

import os,glob
import numpy as np
import statistics as st
import utils.sif_open as sif
import utils.sif_utils as sif_utils


fileType = 0                    # 0: Andor SIF, 1: Andor ASCII, 2: NumPy
fileNameVersion = 1             # for extraction of parameters, 0: V01, 1: V02
FileName = 'Not selected'
SpecImage = []
SpecImage_bak = []
SpecScale = []
PeakLines = []
xPixel = 0
yPixel = 0
xRange1 = 0
xRange2 = 0
BackgroundFixed = False
Background = 0
showRange = 0
lineNr = 0
SpecUnits = 0                   # 0: nm, 1: eV
SwitchRemoveDark = True
SwitchRemoveSpikes = False
Spec2Type = 0                   # 0: None, 1: range, 2: derrivative
SpecClickx = 0
rangeSelected = False
paraNameList = []
seriesParaIndex = 0
pixMaxXY = []
avePtsY = 1
brigthLow =  0
brigthHigh = 255



#Create a list of filenames in Directory
def listFilesInDirectory(Directory, fileType):
    fileNameList = []
    if fileType==0:
        for filename in glob.glob(os.path.join(Directory, '*.sif')):
            fileNameList.append(filename)
    if fileType==1:
        for filename in glob.glob(os.path.join(Directory, '*.asc')):
            fileNameList.append(filename)
    if fileType==2:
        for filename in glob.glob(os.path.join(Directory, '*.npy')):
            if filename.find('_cal') == -1: fileNameList.append(filename) # otherwise calibration file
    if fileType==3:
        for filename in glob.glob(os.path.join(Directory, '*.dat')):
            fileNameList.append(filename)
    return fileNameList


# Load Andor sif file
def LoadAndorSIF(FileName):
    global fileNameVersion, SpecImage, SpecScale, xPixel, yPixel, xRange1, xRange2, Background, BackgroundFixed
    if FileName.find('=') == -1: fileNameVersion = 0
    else                       : fileNameVersion = 1
    data, info = sif.np_open(FileName)              # load raw data-file
    SpecScale = sif_utils.extract_calibration(info)
    SpecImage = data[0]
    xPixel = SpecImage.shape[1]; yPixel = SpecImage.shape[0]
    xRange1 =  SpecScale[0]; xRange2 = SpecScale[xPixel-1]
    Background = 0
    BackgroundFixed = False


# Load Andor ASCII file
def LoadAndorASCII(FileName):
    global fileNameVersion, SpecImage, SpecScale, xPixel, yPixel, xRange1, xRange2, Background, BackgroundFixed
    if FileName.find('=') == -1: fileNameVersion = 0
    else                       : fileNameVersion = 1
    SpecRaw = np.loadtxt(FileName)              # load raw data-file
    SpecRawT = SpecRaw.T                        # transpose row to column
    SpecScale = SpecRawT[0]                     # extract scale
    SpecImage = np.delete(SpecRawT, 0, 0)       # delete scale to generate image
    xPixel = SpecImage.shape[1]; yPixel = SpecImage.shape[0]
    xRange1 =  SpecScale[0]; xRange2 = SpecScale[xPixel-1]
    Background = 0
    BackgroundFixed = False


# Load NumPy file
def LoadNumPy(FileName):
    global fileNameVersion, SpecImage, SpecScale, xPixel, yPixel, xRange1, xRange2, Background, BackgroundFixed
    SpecImage = np.load(FileName)
    cal_FileName = FileName[0:len(FileName)-4]+'_cal.npy'
    SpecScale = np.load(cal_FileName)
    xPixel = SpecImage.shape[1]; yPixel = SpecImage.shape[0]
    xRange1 =  SpecScale[0]; xRange2 = SpecScale[xPixel-2]
    Background = 0
    BackgroundFixed = False


# Detects the line number containing the peaks from all images in the series
def AnalyseImageSeries(fileList, fileType):
    lineNrList = []
    for i in range(len(fileList)):
        if fileType==0: LoadAndorSIF(fileList[i])
        if fileType==1: LoadAndorASCII(fileList[i])
        Background = CalcDark()
        lineNr = DetectLineMaxVal(Background)
        if lineNr>0: lineNrList.append(lineNr)
    NrList = []; NrCount = []
    for i in range(len(lineNrList)):
        Nr = lineNrList[i]
        if Nr in NrList:
            ind = NrList.index(Nr)
            NrCount[ind] = NrCount[ind]+1
        else:
            NrList.append(Nr)
            NrCount.append(1)
    ind = np.argmax(NrCount)
    lineNr = NrList[ind]
    return lineNr


# Detects the variable parameters from a filename
def AnalyzeFileName(fileName):
    global fileNameVersion
    if fileName.find('=') == -1:               # V01: only one variable parameter
        paraNames  = AnalyzeFileNameV01(fileName)
        paraVals = 0    # todo
        fileNameVersion = 0
    else:                                       # V02: multiple variable parameters
        paraNames, paraVals = AnalyzeFileNameV02(fileName)
        fileNameVersion = 1
    return paraNames, paraVals


# Detects the variable parameters from a filename
# First version, only one variable parameter, not further tested
def AnalyzeFileNameV01(fileName):
    range1 = len(fileName); range2 = 0
    # Detects varied range in strings
    for i in range(len(fileList)):
        fileName = fileList[i]
        if fileName != fileName0:
            diffIndList = []
            for n in range(len(fileName)):
                if fileName[n] != fileName0[n]: diffIndList.append(n)
            if min(diffIndList)<range1: range1 = min(diffIndList)
            if max(diffIndList)>range2: range2 = max(diffIndList)
    paraList = []
    for i in range(len(fileList)):
        fileName = fileList[i]
        para = float(fileName[range1:range2-len(fileName)+1])
        paraList.append(para)
    return paraList


# Detects the variable parameters from a filename
# Second version, multiple variable parameters
# Paramers: T= temperature, E= exposure time, P= laser power, U= voltage, A= angle
def AnalyzeFileNameV02(fileName):
    global paraNameList
    fileName = os.path.basename(fileName)           # Remove path
    fileName = fileName[0 : len(fileName)-4]        # Remove extension
    paraList = fileName.split(',')                  # list of parameters: name, val, units
    paraNames = []; paraVals = []
    for i in range(len(paraList)):
        s0 = paraList[i]                            # parameter: name, val, units
        i1 = s0.find('=')
        if i1>=0:
            sn = s0[0 : i1].strip()                 # parameter: name
            paraNames.append(sn)
            svu = s0[i1+1 : len(s0)].strip()        # parameter: value+unit
            sv = ''
            OK = False; i = 0
            while OK==False:
                c = svu[i]
                if c.isdigit() or c in ['-', '.']:
                    sv = sv + c
                    i += 1
                    if i>len(svu)-1: OK = True
                else: OK = True
            paraVals.append(float(sv))              # parameter: value
    paraNameList = paraNames
    return paraNames, paraVals


# Sorts the fileList for increasing parameter values
def sortFileList(fileList, paraNum):
    listVals = []
    for i in range(len(fileList)):
        paraNames, paraVals = AnalyzeFileName(fileList[i])
        val = paraVals[seriesParaIndex]
        listVals.append([i, val])
    listVals_sorted = sorted(listVals, key=lambda x: x[1])
    fileList_sorted = []
    for i in range(len(fileList)):
        index = listVals_sorted[i][0]
        fileList_sorted.append(fileList[index])
    return fileList_sorted


# Gives line values from an detector image
# Averaging along y is supported up to max averY = 20
def getLineVals(image, lineNr, averY):
    xPixel = image.shape[1]; yPixel = image.shape[0]
    if lineNr + (averY//2+1) > yPixel-1: lineNr = yPixel - (averY//2+1) - 1
    if lineNr - (averY//2+1) < 0:        lineNr = (averY//2+1)
    LineVals = []
    for ix in range(xPixel):
        yVal = image[lineNr][ix]
        if (averY > 1):
            if averY > 1: yVal = yVal+image[lineNr+1][ix]
            if averY > 2: yVal = yVal+image[lineNr-1][ix]
            if averY > 3: yVal = yVal+image[lineNr+2][ix]
            if averY > 4: yVal = yVal+image[lineNr-2][ix]
            if averY > 5: yVal = yVal+image[lineNr+3][ix]
            if averY > 6: yVal = yVal+image[lineNr-3][ix]
            if averY > 7: yVal = yVal+image[lineNr+4][ix]
            if averY > 8: yVal = yVal+image[lineNr-4][ix]
            if averY > 9: yVal = yVal+image[lineNr+5][ix]
            if averY > 10: yVal = yVal+image[lineNr-5][ix]
            if averY > 11: yVal = yVal+image[lineNr+6][ix]
            if averY > 12: yVal = yVal+image[lineNr-6][ix]
            if averY > 13: yVal = yVal+image[lineNr+7][ix]
            if averY > 14: yVal = yVal+image[lineNr-7][ix]
            if averY > 15: yVal = yVal+image[lineNr+8][ix]
            if averY > 16: yVal = yVal+image[lineNr-8][ix]
            if averY > 17: yVal = yVal+image[lineNr+9][ix]
            if averY > 18: yVal = yVal+image[lineNr-9][ix]
            if averY > 19: yVal = yVal+image[lineNr+10][ix]
            if averY > 20: yVal = yVal+image[lineNr-10][ix]
            yVal=yVal//averY
        LineVals.append(yVal)
    return LineVals


# Calc dark counts
def CalcDark():
    averY = 1
    image = SpecImage
    yPixel = image.shape[0]
    backgroundVals = getLineVals(image, (averY//2+1)-1, 10)
    aveBackground1 = st.mean(backgroundVals)
    backgroundVals = getLineVals(image, (yPixel-(averY//2+1)-1), 10)
    aveBackground2 = st.mean(backgroundVals)
    if aveBackground1<aveBackground2:
        aveBackground = aveBackground1
    else:
        aveBackground = aveBackground2
    return aveBackground


# Detects the pixel with max intensity
def DetectPixMaxVal(Image):
    global pixMaxXY
    maxValIndexFlat = np.argmax(Image)
    xPixel = Image.shape[1]; yPixel = Image.shape[0]
    maxValIndex = np.unravel_index(maxValIndexFlat, (yPixel,xPixel))
    pixMaxXY = maxValIndex
    return pixMaxXY


def RemoveSpikes(Image):
# for NumPy file images
    global SpecImage, lineNr, brigthLow, brigthHigh
    threshold = 5
    SpecImage = Image
    xPixel = Image.shape[1]; yPixel = Image.shape[0]
    Background = CalcDark()
    OK = False
    loops = 0
    while OK == False:
        pixMaxXY = DetectPixMaxVal(Image)
        xp = pixMaxXY[1]; yp = pixMaxXY[0]
        pixMaxVal = SpecImage[yp][xp]-Background
        ave = 0
        if xp>0: xp1 = xp-1
        else: xp1 = xp+1
        ave = ave+SpecImage[yp][xp1]-Background
        if xp<xPixel-1: xp1 = xp+1
        else: xp1 = xp-1
        ave = ave+SpecImage[yp][xp1]-Background
        if yp>0: yp1 = yp-1
        else: yp1 = yp+1
        ave = ave+SpecImage[yp1][xp]-Background
        if yp<yPixel-1: yp1 = yp+1
        else: yp1 = yp-1
        ave = (ave+SpecImage[yp1][xp]-Background)/4
        if pixMaxVal > threshold*ave: SpecImage[yp][xp] = ave+Background
        else: OK = True
        pixMaxVal = SpecImage[yp][xp]
        loops = loops+1
        if loops>20: OK = True
    brigthLow = Background
    brigthHigh = SpecImage.max()
    lineNr = DetectLineMaxVal(Background)
    CreateSpec(Image, lineNr)
    return SpecImage


# Detects the line with max intensity
def DetectLineMaxVal(Background):
    global lineNr
    linIndMaxVal = np.argmax(SpecImage)
    xPixel = SpecImage.shape[1]; yPixel = SpecImage.shape[0]
    indMaxVal = np.unravel_index(linIndMaxVal, (yPixel,xPixel))
    lineMaxVal = indMaxVal[0]; xMaxVal = indMaxVal[1]
    maxVal =  SpecImage[lineMaxVal,xMaxVal]-Background
    if maxVal<10: lineMaxVal = 0
    lineNr = lineMaxVal
    return lineMaxVal


def doTilting(tiltPix):
    global SpecImage
    # SpecImage[0][0] is at the left bottom corner
    SpecImage = SpecImage_bak.copy()
    tiltPix = int(tiltPix)
    if tiltPix != 0:
        xpMax = xPixel-1
        for xp in range(0, xPixel-1):
            for yp in range(0, yPixel-1):
                new_yp = yp + (tiltPix/2)*(xp-(xpMax/2))/(xpMax/2)-1
                new_yp1 = int(new_yp)
                new_yp2 = new_yp1+1
                if (new_yp1>0) and (new_yp2<yPixel-1):
                    val1 = SpecImage_bak[new_yp1][xp]
                    val2 = SpecImage_bak[new_yp2][xp]
                    new_val = abs(new_yp1-new_yp)*val2 + abs(new_yp2-new_yp)*val1
                    SpecImage[yp][xp] = new_val


# Create spectrum from image
def CreateSpec(Image, lineNr):
    global Background
    Background = CalcDark()
    SpecVals2 = getLineVals(SpecImage, lineNr, avePtsY)
    if SwitchRemoveDark == True: SpecVals2 = SpecVals2 - Background
    SpecScale2 = SpecScale
    if SpecUnits == 1: SpecScale2  = 1240/SpecScale2
    while len(SpecVals2)>len(SpecScale2): SpecVals2 = SpecVals2[:-1]
    return SpecScale2, SpecVals2


# Calc derivative
def CalcDerivative():
    SpecVals = SpecImage[lineNr]
    SpecScale2 = SpecScale
    if SpecUnits == 1:
        SpecScale2 = 1240/SpecScale2
    dx = np.gradient(SpecScale2); dy = np.gradient(SpecVals); deriv = dy/dx
    dx2 = np.gradient(dx); dy2 = np.gradient(dy); deriv2 = dy2/dx
    return SpecScale2, deriv2
    #return SpecScale2, deriv


# Integrate
def Integrate():
    SpecScale, SpecVals = CreateSpec()
    sumVal = 0
    for ix in range(0, len(SpecVals)-1):
        dX = abs(SpecScale[ix]-SpecScale[ix+1])
        dY = SpecVals[ix]
        sumVal = sumVal + dX*dY
    return sumVal


# Load file
def LoadFile(FileName):
    global Background, lineNr, brigthLow, brigthHigh
    if fileType == 0: LoadAndorSIF(FileName)
    if fileType == 1: LoadAndorASCII(FileName)
    if fileType == 2: LoadNumPy(FileName)
    Background = CalcDark()
    if SwitchRemoveSpikes: RemoveSpikes(SpecImage)
    lineNr = DetectLineMaxVal(Background)
    brigthLow = Background
    brigthHigh = SpecImage.max()

