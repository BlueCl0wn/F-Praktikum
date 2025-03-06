import numpy as np

from DatFileReader import DatFileReader
from Fehlerrechnung import *
from scipy.signal import find_peaks
from uncertainties.umath import sin, cos, sqrt
import uncertainties.unumpy as unp
from scipy.optimize import fsolve


# Tupleaufbau für graph() im multiple modus:
# (data array, label, plot type, marker, linewdiths)

# Ermöglicht Ausschalten des Plottens nach Thema.
plot = False
plot1 = False
plot2 = False
plot3 = False
plot4 = False
plot5 = False
plot6 = False
plot7 = False


def graph_spect(Data_Inst: DatFileReader, **kwargs) -> None:
    """
    Standardisierte Plotfunktion zum Darstellen der ganzen Spektraldaten.
    :param Data_Inst: Instanz von DatFileReader
    :return: None
    """
    graph(Data_Inst.x_data / 1000, Data_Inst.y_data, graph="plot",
          xlabel=r"Frequenz / $kHz$", ylabel=r"Intensität / $dBm$", **kwargs)


# ------------------ 1. Kontrastmessung--------------------
print(" 1. Kontrastmessug ".center(100, "-"))

# AC Messung Bild
Ramp_AC = DatFileReader(r"../Messwerte/Oszi_Ramp_AC.CSV", header_lines=25)

y_data = [(Ramp_AC.y_data[0], "Sinus" ,"plot" , "x" , 0.2),
          (Ramp_AC.y_data[2], "Ramp" ,"plot" , "x" , 0.2)]

if plot1 or plot:
    graph(Ramp_AC.x_data, y_data, multiple=True, ylabel=rf"Spannung / $mV$", xlabel=rf"Zeit / $ms$")

# DC Messung Kontrast
Ramp_DC = DatFileReader("../Messwerte/Oszi_Ramp_DC.CSV", header_lines=25)
y_data = [(Ramp_DC.y_data[0], "Sinus" ,"plot" , "x" , 0.2),
          (Ramp_DC.y_data[2], "Ramp" ,"plot" , "x" , 0.2)]
if plot1 or plot:
    graph(Ramp_DC.x_data, y_data, multiple=True, ylabel=rf"Spannung / $mV$", xlabel=rf"Zeit / $ms$")
    graph(Ramp_DC.x_data, Ramp_DC.y_data[0], graph="plot", ylabel=rf"Spannung / $mV$", xlabel=rf"Zeit / $ms$", size=0.1, minorgrid = True)
    graph(Ramp_DC.x_data, Ramp_AC.y_data[0], graph="plot", ylabel=rf"Spannung / $mV$", xlabel=rf"Zeit / $ms$", size=0.1, minorgrid = True)

I_max = unc.ufloat(-0.1 + 0.05/4, 0.025/2 )
I_min = unc.ufloat(-1.1, 0.025)

def Kontrast(I_1, I_2):
    return (I_1 - I_2)/(I_2 + I_1)
print(f"I_min = {I_min}, I_max = {I_max}, Kontrast C = {Kontrast(I_min, I_max)}")

# Oszi Messung Kontrast im Vakuum. (deshalb noch Schwingung der Membran)
Ramp_DC_Vakuum = DatFileReader("../Messwerte/Oszi_Ramp_DC_Vakuum.CSV", header_lines=25)
y_data = [(Ramp_DC_Vakuum.y_data[0], "Sinus" ,"plot" , "x" , 0.2),
          (Ramp_DC_Vakuum.y_data[2], "Ramp-Spannung" ,"plot" , "x" , 0.2)]
if plot1 or plot:
    graph(Ramp_DC_Vakuum.x_data, y_data, multiple=True, ylabel=rf"Spannung / $mV$", xlabel=rf"Zeit / $ms$")


# ------------------ 2. Übersichtsmessung    --------------------
print()
print(" 2. Übersichtsmessung der Moden   ".center(100, "-"))

# TODO: finish. Is it necessary to add modes? If so, what does that even mean?


ubersicht = DatFileReader("../Messwerte/FileCheck_010.DAT", header_lines=29)
peaks_ubersicht, _ = find_peaks(ubersicht.y_data, prominence=0.4)  # find peaks
if plot2 or plot:
    graph_spect(ubersicht, peaks=peaks_ubersicht, size=0.5)

print()
# ------------------ 3. Bestimmung der Kalibrationskonstante    --------------------
print(" 3. Bestimmung der Kalibrationskonstante ".center(100, "-"))



# Wellelänge des benutzten Lasers
l = 660e-9 # m


def f(x:float,_a: float, _b: float)-> float:
    return _a+_b*cos(x/l)^2

def f_deriv(x:float, _b: float)-> float:
    return -(2 * _b * cos(x / l) * sin(x / l)) / l

V_min = unc.ufloat(-4.5e-3, 0.5e-3) # V
V_max = unc.ufloat(-5.5e-3, 0.5e-3) # V
a = V_min
b = V_max - a
x = l/8
kali_kons = f_deriv(x, b)
print("Kalibrationskostante K =", kali_kons)

#  sum_value.derivatives[u])


print()
# ------------------ 4. Weglängenänderung    --------------------
print(" 4. Weglängenänderung ".center(100, "-"))


def x_d(_P, _R, _K):
    _U = sqrt(_P*_R)
    return _U/_K

def P_d(_I):
    P_0 = 1e-3 # W
    return P_0 * 10**(0.1*_I)

Kalibrationsdaten = DatFileReader("../Messwerte/FileCheck_013.DAT")
peaks_kalibrat, _ = find_peaks(Kalibrationsdaten.y_data, prominence=0.7)  # find peaks
print("Peak der Integration bei:", Kalibrationsdaten[peaks_kalibrat[0]])
if plot4 or plot:
    graph_spect(Kalibrationsdaten, peaks=peaks_kalibrat)

P = P_d(Kalibrationsdaten[peaks_kalibrat[0]][1])
R = 50 # Ohm
dx = x_d(P, R, kali_kons)
print("Weglängenänderung: ", dx)



print()
# ------------------ 5. Vergleichsbild Mode bei verschiedenen Drücken --------------------
print(" 5. Vergleichsbild Moden bei verschiedenen Drücken ".center(100, "-"))

# TODO: The plots are not on the same level. This is probably due to different Reference Levels #
#       But how is it possible to adjust them to one value?

# Mode 1
Mode_1_Pmin = DatFileReader("../Messwerte/FileCheck_015.DAT", header_lines=29)
Mode_1_Pmid = DatFileReader("../Messwerte/FileCheck_029.DAT", header_lines=29)
Mode_1_Pmax = DatFileReader("../Messwerte/FileCheck_026.DAT", header_lines=29)
y_data_Mode_1 = ((Mode_1_Pmin.y_data, r"$P = 3 \cdot 10^{-6} ~ mBar$", "plot", "-", 1),
                 (Mode_1_Pmid.y_data, r"$P = 1 \cdot 10^{-4} ~ mBar$", "plot", "-", 1),
                 (Mode_1_Pmax.y_data, r"$P = 6,5 \cdot 10^{-3} ~ mBar$", "plot", "-", 1))
#                (data array, label, plot type, marker, linewdiths)

if plot5 or plot:
    graph(Mode_1_Pmid.x_data / 1000, y_data_Mode_1, multiple=True, xlabel=r"Frequenz / $kHz$", ylabel=r"Intensität / $dBm$")
print(Mode_1_Pmax.get_header_value("Ref Level"))
# Mode 2
Mode_2_Pmin = DatFileReader("../Messwerte/FileCheck_016.DAT", header_lines=29)
Mode_2_Pmid = DatFileReader("../Messwerte/FileCheck_030.DAT", header_lines=29)
Mode_2_Pmax = DatFileReader("../Messwerte/FileCheck_027.DAT", header_lines=29)
y_data_Mode_2 = ((Mode_2_Pmin.y_data, r"$P = 3 \cdot 10^{-6} ~ mBar$", "plot", "-", 1),
                 (Mode_2_Pmid.y_data, r"$P = 1 \cdot 10^{-4} ~ mBar$", "plot", "-", 1),
                 (Mode_2_Pmax.y_data, r"$P = 6,5 \cdot 10^{-3} ~ mBar$", "plot", "-", 1))

if plot5 or plot:
    graph(Mode_2_Pmid.x_data / 1000, y_data_Mode_2, multiple=True, xlabel=r"Frequenz / $kHz$", ylabel=r"Intensität / $dBm$")




print()
# ------------------ 6. Ring Down Messungen --------------------
print(" 6. Ring Down Messungen".center(100, "-"))

fits_gamma = []
def ring_down_fast(Data, start, stop):
    # Calculate start stop indices of trendlinie based on given x values
    i_start, i_stop = Data.get_index_for_x(start), Data.get_index_for_x(stop)

    # plot Ring Down Messung
    if plot6 or plot:
        #ring_down_one(Data, i_start, i_stop)
        graph(Data.x_data, Data.y_data, xlabel=r"Zeit / $s$", ylabel=r"Intensität / $dBm$", trendlinie=True,
              graph="plot", trend_start=i_start, trend_stop=i_stop, minorgrid=True)

    # Separately save fit slope with std and print fit data.
    vars = poly_fit(Data.x_data[i_start: i_stop], Data.y_data[i_start: i_stop], uncert=True)
    fits_gamma.append(vars[0])
    print(f"{vars[0]} * x + {vars[1]}")

RingDown_01 = DatFileReader("../Messwerte/FileCheck_014.DAT", header_lines=29)
RingDown_02 = DatFileReader("../Messwerte/FileCheck_017.DAT", header_lines=29)
RingDown_1 = DatFileReader("../Messwerte/FileCheck_018.DAT", header_lines=29)
RingDown_2 = DatFileReader("../Messwerte/FileCheck_019.DAT", header_lines=29)
RingDown_3 = DatFileReader("../Messwerte/FileCheck_020.DAT", header_lines=29)
RingDown_4 = DatFileReader("../Messwerte/FileCheck_021.DAT", header_lines=29)
RingDown_5 = DatFileReader("../Messwerte/FileCheck_022.DAT", header_lines=29)
RingDown_6 = DatFileReader("../Messwerte/FileCheck_023.DAT", header_lines=29)
RingDown_7 = DatFileReader("../Messwerte/FileCheck_024.DAT", header_lines=29)
RingDown_8 = DatFileReader("../Messwerte/FileCheck_025.DAT", header_lines=29)
RingDown_9 = DatFileReader("../Messwerte/FileCheck_028.DAT", header_lines=29)



frequenzen = np.array([261660, 261389, 261394, 261395, 261405, 261394, 261395, 261376, 261400]) # Hz
drucks = np.array([1.4e-6, 7.1e-6, 1.5e-5, 7.8e-5, 1.6e-4, 5.8e-4, 1.5e-3, 4.6e-3, 9.6e-3])  # mBar
print("drucks.size", drucks.size)

#print(RingDown_2.get_index_for_x(3.53), ",", RingDown_2.get_index_for_x(7.5))
print("Fits der linearen Teile der Ring Down Messungen:")
#ring_down_fast(RingDown_01, 2.43, 2.95) # Sobald diese beiden nicht mehr kommentiert sind, crasht der Code, da diese nicht Teil der eigentlichen Messung sind.
#ring_down_fast(RingDown_02, 3.53 , 7.5)
ring_down_fast(RingDown_1, 2.5 , 6.5)
ring_down_fast(RingDown_2, 1.8 , 5.5)
ring_down_fast(RingDown_3, 2.2 , 6)
ring_down_fast(RingDown_4, 2.5 , 5.5)
ring_down_fast(RingDown_5, 2.3 , 5.5)
ring_down_fast(RingDown_6, 2.25 , 4.5)
ring_down_fast(RingDown_7, 2, 3.5)
ring_down_fast(RingDown_8, 0.95, 1.5)
ring_down_fast(RingDown_9, 0.8, 1.1)
print()
# ------------------ 7. Ausmessen und Plotten Gütefaktoren --------------------
print(" 7. Ausmessen und Plotten Gütefaktoren".center(100, "-"))

def guetefaktor(F, Gamma) -> int:
    """ Method doing quality factor calculation.
    Gütefaktor ist einheitslos"""
    return F/Gamma

fits_gamma = np.array(fits_gamma)

#print("fits_gamma", fits_gamma)
guetefaktoren = guetefaktor(frequenzen, -fits_gamma) # Einheitslos
guetefaktoren = unp.uarray([x.nominal_value for x in guetefaktoren],
                       [x.std_dev for x in guetefaktoren])
#print(guetefaktoren)
print("Gütefaktoren:")
print(guetefaktoren)
print()
print("Gütefaktoren.nomial_values:", unp.nominal_values(guetefaktoren))
print()
print("Gütefaktoren.std_devs:", unp.std_devs(guetefaktoren))
for i in guetefaktoren:
    print(i)


if plot7 or plot:
    errors = [i.std_dev for i in guetefaktoren]

    y_guete = [i.nominal_value for i in guetefaktoren]
    graph(drucks, y_guete, yerror=errors, xlabel=r"Druck / $mBar$",
          ylabel=r"Gütefaktor Q")
    graph(drucks, y_guete, yerror=errors, xlabel=r"Druck / $mBar$",
          ylabel=r"Gütefaktor Q", xlog=True)

    # Ich wollte Fehlerbalken hinzufügen, aber die sind so klein, dass man die nicht sehen kann.
    """    
    graph(drucks, y_guete, yerror=errors, xlabel=r"Druck / $mBar$",
          ylabel=r"Gütefaktor Q", graph="errorbar", capsize=3, fmt="r--o", ecolor = "black")
    graph(drucks, y_guete, yerror=errors, xlabel=r"Druck / $mBar$",
          ylabel=r"Gütefaktor Q", xlog=True, graph="errorbar", capsize=3, fmt="r--o", ecolor = "black")
    """
