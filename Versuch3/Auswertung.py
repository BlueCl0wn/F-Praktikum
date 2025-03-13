from Fehlerrechnung import poly_fit
import numpy as np
import math
from uncertainties.umath import sqrt
from uncertainties import unumpy as unp
import uncertainties as unc
from scipy.constants import c



error_guete = 10e6/ 1e5
print("Error_Guete = ", error_guete)


error_ubersicht = (8.5e9 - 9e3)/ 1e5
print("Error_ubersicht = ", error_ubersicht)

# --------------- Radius Bestimmung ----------------------------------
def radius_durch_omega(w, p, l, J) -> float:
    return J/ sqrt((w/c)**2 + (p* math.pi /l)**2)

def omega_durch_radius(a, p, l, J):
    return c * sqrt((J/a)**2 + (p* math.pi/ l)**2)


def f(w):
    return w/(2 * math.pi)

def w(f):
    return 2 * math.pi * f


# ----------------- Bestimmung der Güte ------------------
def kappas_berechhnung(_p_0):
    """
    Berechnet die \kappa für die Güteberechnung
    :param _p_0:
    :return:
    """
    return abs((1+ _p_0)/(1-_p_0)), abs((1- _p_0)/(1+_p_0))

def p_d_halbe_berechnung(_kappas : tuple):
    """
    Berechnet den Wert für \rho an dem die Frequenzen für \Delta \omega abzulesen sind.
    :param _kappas:
    :return:
    """
    def p_d_halb_f(_kappa):
        return sqrt(_kappa**2 + 1)/ (_kappa + 1)
    p_d_halb1 = p_d_halb_f(_kappas[0])
    p_d_halb2 = p_d_halb_f(_kappas[1])
    assert round(p_d_halb1.nominal_value, 10) ==  round(p_d_halb2.nominal_value, 10)
    return p_d_halb1

def Guete(_w_0, _delta_w):
    return _w_0 / _delta_w

def Guete_1(_Q, _kappas):
    return _Q*(1+ _kappas[0]), _Q*(1+ _kappas[1])



# ---------------------- Hohlraumresonator ------------------------------

print("----- Hohlraumresonator".center(100, "-"))
J_010 = 2.40482
J_020 = J_010 * 2

# 9kHz bis 8,8GHz

print()
print("----- Radiusbestimmung:")
f_cavity_grundmode = unc.ufloat(2.997306e9, error_ubersicht) # Hz, abgelesen am VNA
w_cavity_grundmode = w(f_cavity_grundmode)
print(f"Frequenz der grundmode: {f_cavity_grundmode:L} Hz, Omega der Grundmode: {w_cavity_grundmode:L}")
r_cavity = radius_durch_omega(w_cavity_grundmode, 0, 1, J_010)
print(f"Radius der Cavity: {r_cavity:L} m")
w_cavity_mode_2 = radius_durch_omega(r_cavity, 0, 1, J_020)
print(f"Omega der 2 Mode der Cavity: {w_cavity_mode_2:L} Hz")
print(f"Frequenz der 2 Mode der Cavity: {f(w_cavity_mode_2):L} Hz")

print()
print("----- Gütebestimmung:")

print("error guete",error_guete)
w_cavity_grundmode = w(unc.ufloat(2.996926e9, error_guete))
p_w_o_cavity = unc.ufloat(15, 1)
print(f"p(w_0) der cavity ist: {p_w_o_cavity:L}")
kappas_cavity = kappas_berechhnung(p_w_o_cavity)
print(f"Die \kappa der Cavity sind {kappas_cavity}")
p_d_halbe_cavity = p_d_halbe_berechnung(kappas_cavity)
print(f"p für \Delta \omega Bestimmung ist: {p_d_halbe_cavity:L}")

delta_f_cavity = unc.ufloat(2.997514e9-2.996335e9, 2*error_ubersicht)
delta_omega_cavity = w(delta_f_cavity)
print(f"delta halb frequenz cavity: {delta_f_cavity:L} Hz, delta halb omega cavity: {delta_omega_cavity:L} Hz")
Q_cavity = Guete(w_cavity_grundmode, delta_omega_cavity)
Q_cavity_n = Guete_1(Q_cavity, kappas_cavity)
print(f"Cavity: Q = {Q_cavity}, Q_n = {Q_cavity_n}")

print()
print("----- Störkörpermessung:")
## ----------------- Störkörpermessung --------------------
R = np.arange(3.3, 7.6, 0.3) # gemessene Widerstände für z bestimmung de z-Position
R_error = np.full(shape=R.shape,  fill_value=0.1, dtype=float)
R_unp = unp.uarray(R, R_error)
print("R:", R)
R_kali = [0.7, 8.9]
R_kali_error = np.array([0.1, 0.1])
z_kali = [0, 10]
z_kali_error = np.array([0.1, 0.2])
z_vars = poly_fit(z_kali, R_kali,y_error=R_kali_error ,  uncert=True)
print("störmessung fit werte: ", z_vars)
z = poly_fit(z_kali, R_kali,y_error=R_kali_error ,  return_func=True)
Z = z(R_unp)
print("z:", Z)
# Hier habe ich x und y achse beim fitten verwechselt.
# eigentlich Falsch, aber der Betreuer hat es abgenickt, also lassen wir es so.

"""
z = poly_fit([0.7, 8.9],[0, 11-1],   return_func=True)
Z = z(R)
print(z(0.7))
print("z:", Z)
"""

print()
print()
print()
# ---------------------- Buncher ------------------------------

print("----- Buncher".center(100, "-"))

# Radiusbestimmung
print()
print("----- Radiusbestimmung:")
f_buncher_grundmode = unc.ufloat(3.009462e9, error_ubersicht) # Hz, abgelesen am VNA

w_buncher_grundmode = w(f_buncher_grundmode)
print(f"Frequenz der grundmode: {f_buncher_grundmode:L} Hz, Omega der Grundmode: {w_buncher_grundmode:L}")
r_buncher = radius_durch_omega(w_buncher_grundmode, 0, 1, J_010)
print(f"Radius des Bunchers: {r_buncher:L} m")
w_buncher_mode_2 = radius_durch_omega(r_buncher, 0, 1, J_020)
print(f"Omega der 2 Mode des Bunchers: {w_buncher_mode_2:L} Hz")
print(f"Frequenz der 2 Mode des Bunchers: {f(w_buncher_mode_2):L} Hz")


print("---- Gütebestimmung:")

w_buncher_grundmode = w(unc.ufloat(2.996926e9, error_guete))
p_w_o_buncher = unc.ufloat(68, 1)
p_w_o_buncher = unc.ufloat(110, 2)
print(f"p(w_0) der buncher ist: {p_w_o_buncher:L}")
kappas_buncher = kappas_berechhnung(p_w_o_buncher)
print(f"Die \kappa der buncher sind {kappas_buncher}")
p_d_halbe_buncher = p_d_halbe_berechnung(kappas_buncher)
print(f"p für \Delta \omega Bestimmung ist: {p_d_halbe_buncher:L}")

delta_f_buncher = unc.ufloat(abs(3.008646e9-3.010370e9), 2*error_ubersicht)
delta_omega_buncher = w(delta_f_buncher)
print(f"delta halb frequenz buncher: {delta_f_cavity:L} Hz, delta halb omega buncher: {delta_omega_buncher:L} Hz")
Q_buncher = Guete(w_buncher_grundmode, delta_omega_buncher)
Q_buncher_n = Guete_1(Q_buncher, kappas_buncher)
print(f"Buncher: Q = {Q_buncher} Hz, Q_n = {Q_buncher_n}")



# ---------------------- Lichtgeschwindigkeit ------------------------------

print("----- Lichgeschwindigkeit".center(100, "-"))

def calc_c(L_1, L_real):
    return L_real/L_1


#Kabel 1
print()
print("----- Kabel 1")
L_fit_1 = unc.ufloat(1.71650457, 0.00000005, "m") # cm
L_winkel_1 = unc.ufloat(1.7, 0.020, "m") # m
L_mess_1 = unc.ufloat(1.24, 0.015, "m") #m

c_winkel_1 = calc_c(L_winkel_1, L_mess_1)
c_fit_1 = calc_c(L_fit_1, L_mess_1)
print(f"Kabel1: c_winkel_1: {c_winkel_1:L}, c_fit_1: {c_fit_1:L}")

#Kabel 2
print()
print("----- Kabel 2")


L_fit_2 = unc.ufloat(1.52541016, 0.00000007, "m") # m
L_winkel_2 = unc.ufloat(1.51, 0.030, "m") # m
L_mess_2= unc.ufloat(1.005, 0.015, "m") # m

c_winkel_2 = calc_c(L_winkel_2, L_mess_2)
c_fit_2 = calc_c(L_fit_2, L_mess_2)
print(f"Kabel2: c_winkel_2: {c_winkel_2:L}, c_fit_2: {c_fit_2:L}")