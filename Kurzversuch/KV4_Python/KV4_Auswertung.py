import numpy as np
import scipy as sp
import uncertainties as unc
from matplotlib.pyplot import xlabel
from scipy import signal
from uncertainties import unumpy as unp
import uncertainties.umath as umath
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks_cwt
import Fehlerrechnung as Fr
from Funktionen import *
Project_Path = "C:/Users/darek/OneDrive - M365 Universität Hamburg/UNI/FPrak/F_Praktikum/Kurzversuch/"

end_of_data = 1200
start_of_data = 0
# C:\Users\darek\OneDrive - M365 Universität Hamburg\UNI\FPrak\F_Praktikum\Kurzversuch\Messwerte_KV4\4-2\dunkelspektrum-57V_6,5Mio.txt
# F_Praktikum\Kurzversuch\Messwerte_KV4\4-2\dunkelspektrum-57V_6,5Mio.txt
#KurzversuchMesswerte_KV4/4-2/dunkelspektrum-57V_6,5Mio.txt
dunkel_57 = np.loadtxt(Project_Path + "Messwerte_KV4/4-2/dunkelspektrum-57V_6,5Mio.txt", skiprows=1)[start_of_data:end_of_data].transpose()
dunkel_60 = np.loadtxt(Project_Path + "Messwerte_KV4/4-2/dunkelspektrum-60V_5,5Mio.txt", skiprows=1)[start_of_data:end_of_data].transpose()
dunkel_63 = np.loadtxt(Project_Path + "Messwerte_KV4/4-2/dunkelspektrum-63V_5Mio.txt", skiprows=1)[start_of_data:end_of_data].transpose()

dunkel_arr = np.array([dunkel_57, dunkel_60, dunkel_63])
voltage_dunkel_arr = np.array([57,60,30])

gate_8 = np.loadtxt(Project_Path + "Messwerte_KV4/4-1-5/4.5 Histogram mit Gate 8ns.txt", skiprows=1)[start_of_data:end_of_data].transpose()
gate_7000 = np.loadtxt(Project_Path + "Messwerte_KV4/4-1-5/4.5 Histogram mit Gate 7000ns.txt", skiprows=1)[start_of_data:end_of_data].transpose()
gate_arr = np.array([8,7000])
gate_hist_arr = np.array([gate_8, gate_7000])

led_55 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-55V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_56 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-56V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_57 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-57V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_58 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-58V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_59 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-59V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_60 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-60V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_61 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-61V.txt", skiprows=1)[start_of_data:end_of_data].transpose()
led_62 = np.loadtxt(Project_Path + "Messwerte_KV4/4-3/led-spektrum-62V.txt", skiprows=1)[start_of_data:end_of_data].transpose()

spectrum_arr = (np.array([led_55, led_56, led_57, led_58, led_59, led_60, led_61, led_62]))
voltage_led_arr = np.arange(55, 63)


def get_index_peak(spectrum, peak_nr):
    peaks = find_peaks_cwt(spectrum[1], widths=np.array([10,11, 12, 13, 15, 20, 30]))
    return peaks[peak_nr]

def get_cutout_of_peak(spectrum, peak_nr):
    p0, p1, p_n = get_index_peak(spectrum, np.array([0, 1, peak_nr])) # index of peak 0
    #p1 = peaks[1] # index of peak 1
    #p_n = peaks[peak_nr]
    d = int((p1 - p0) / 2) # estimated gain

    # Cutouts of spectrum to use for curve_fit
    if p_n-d < 0:
        cutout = spectrum[:, 0:p_n + d]
    else:
        cutout = spectrum[:, p_n - d:p_n + d]
    return cutout

def events_pedestal(spectrum, peak_nr):
    cutout = get_cutout_of_peak(spectrum, peak_nr)
    #Fr.graph(*cutout)
    return cutout[1].sum()




def get_gain(spectrum, voltage = None, **kwargs):
    defaultKwargs = {'plot': False, 'printt': False}
    kwargs = {**defaultKwargs, **kwargs}

    peaks = find_peaks_cwt(spectrum[1], widths=np.array([10,11, 12, 13, 15, 20, 30]))

    """
    print(voltage)
    print("peak indices: ", peaks)
    print("peak ADC-Channel:", spectrum[0][peaks])
    print("peaks ADC-Counts: ", spectrum[1][peaks])
    print()
    """

    p0, p1 = get_index_peak(spectrum, np.array([0,1]))
    #d = int((p1 - p0) / 2) # estimated gain half

    #y_1_new = spectrum[:, p1 - d:p1 + d]
    y_0_new = get_cutout_of_peak(spectrum, 0)
    y_1_new = get_cutout_of_peak(spectrum, 1)

    # Scaling ratios t get better conditions numbers
    scale0 = y_0_new[1].max() * 1
    scale1 = y_1_new[1].max() * 1

    init_guess_0 = [spectrum[0, p0], 10, 30]

    peak_0_gauss_uf = gauss_fit(y_0_new[0], y_0_new[1] / scale0, p0=init_guess_0)

    init_guess_1 = [spectrum[0,p1], *[i.nominal_value for i in peak_0_gauss_uf][1:]]

    peak_1_gauss_uf = gauss_fit(y_1_new[0], y_1_new[1] / scale1, p0=init_guess_1)

    # Calculate fitted y data in form of arrays
    y_gauss_0 = gaussian(spectrum[0], *[i.nominal_value for i in peak_0_gauss_uf])
    y_gauss_1 = gaussian(spectrum[0], *[i.nominal_value for i in peak_1_gauss_uf])

    # calculated gain
    gain = peak_1_gauss_uf[0] - peak_0_gauss_uf[0]
    # print("Gain = ", gain)

    if kwargs["plot"] is True:
        # creation of plot tuple for usage with homemade graph method.
        plots = ((spectrum[1], "Messwerte", "scatter", ".", 1.5), (y_gauss_0*scale0, "Gauss beim 0. Peak", "plot", None, 1),
                 (y_gauss_1 *scale1, "Gauss beim 1. Peak", "plot", None,  1))

        Fr.graph(spectrum[0], plots, ylog=False, ylabel="ADC Counts", xlabel="ADC Channel",
                 title=rf"LED-Spektrum bei bei BiasVoltage von ${voltage}V$", marker=".")


    if kwargs['printt'] is True:
        print(voltage, ":")
        print("Parameter for peak 0: ", peak_0_gauss_uf, "\n")
        print("Parameter for peak 1: ", peak_1_gauss_uf, "\n")
        print("Gain = ", gain)
        print()
        print("-----------")

    return gain


def get_gain_fit():
    gain_arr = np.array([get_gain(led_spectrum, voltage) for led_spectrum, voltage in zip(spectrum_arr, voltage_led_arr)])

    gain_arr_nom = [i.nominal_value for i in gain_arr]
    gain_arr_std = [i.std_dev for i in gain_arr]

    gain_fit_params = poly_fit(voltage_led_arr, gain_arr_nom, yerror=gain_arr_std)
    print(gain_arr)
    plots = ((gain_arr_nom, "gain", "errorbar", ".", 1.5, gain_arr_std),
             (lin(voltage_led_arr, *gain_fit_params[0]), rf"Gain-Fit, ${gain_fit_params[0][0]:2.1f}+-{gain_fit_params[1][0]:.1g} \dot x + {gain_fit_params[0][1]:3.0f}+-{gain_fit_params[1][1]:.1g}$", "plot", None, 1))
    Fr.graph(voltage_led_arr, plots, ylabel="Gain", xlabel="Voltage", title=rf"Gain gefittet nach der angelegten Spannung")
    print(f"Gain-Fit, {gain_fit_params[0][0]}+-{gain_fit_params[1][0]} * x + {gain_fit_params[0][1]}+-{gain_fit_params[1][1]}")
    return None

#get_gain_fit()

def get_mean_poisson(spectrum, kind="continous") -> unc.Variable |np.ndarray:

    def get_mean_poisson_singel_cont(spectrum):
        f_0 = events_pedestal(spectrum, 0)
        f_0_uf = unc.ufloat(f_0, np.sqrt(f_0))
        f_ges = spectrum[1].sum()
        f_ges_uf = unc.ufloat(f_ges, np.sqrt(f_ges))
        #print("f_0_uf: ", f_0_uf)
        return -umath.log(f_0_uf / f_ges_uf)

    def get_mean_poisson_singel_disc(spectrum):
        f_0 = spectrum[1][0] # events_pedestal(spectrum, 0)
        f_0_uf = unc.ufloat(f_0, np.sqrt(f_0))
        f_ges = spectrum[1].sum()
        f_ges_uf = unc.ufloat(f_ges, np.sqrt(f_ges))
        return -umath.log(f_0_uf / f_ges_uf)

    if kind == "continous":
        get_mean_poisson_single = get_mean_poisson_singel_cont
    elif kind == "discrete":
        get_mean_poisson_single = get_mean_poisson_singel_disc


    if spectrum.ndim == 2: # single spectrum

        lam = get_mean_poisson_single(spectrum)
        return lam
    elif spectrum.ndim == 3: # array of spectrums
        lams = np.array([get_mean_poisson_single(i) for i in spectrum])
        return lams


#print(get_mean_poisson(led_55))
#print(get_mean_poisson(spectrum_arr))
#print()
def bin_data(spectrum, print=False):
    peaks = find_peaks_cwt(spectrum[1], widths=np.array([10,11, 12, 13, 15, 20, 30]))
    d = peaks[1]-peaks[0]
    bins = np.arange(peaks[0] - d/2, peaks[-1] + d/2, d)
    y = np.histogram(spectrum[1], bins)[0]
    if print:
        plt.hist(spectrum[1], bins)
        plt.show()
    return y, bins

def get_poisson_from_hist(spectrum, **kwargs):
    defaultKwargs = {'p0': None}
    kwargs = {**defaultKwargs, **kwargs}

    peaks = find_peaks_cwt(spectrum[1], widths=np.array([10,11, 12, 13, 15, 20, 30]))
    d = peaks[1]-peaks[0]
    bins = np.arange(peaks[0] - d/2, peaks[-1] + d/2, d)
    #y = np.histogram(spectrum[1], bins)[0]
    y = plt.hist(spectrum[1]/spectrum[1].sum(), bins/spectrum[1].sum())[0]
    #fit = get_poisson_from_hist(led_55, p0=kwargs["p0"])
    fit_params = poisson_fit(y, bins[:-1], p0=kwargs["p0"])
    #plt.plot(spectrum[0], poisson(led_55[0], [i.nominal_value for i in fit_params][0]))
    plt.show()
    return fit_params

LED_Spektrum = True
if LED_Spektrum:
    print("gains:")
    [get_gain(spectrum_arr_i, v_i, printt=True) for spectrum_arr_i, v_i in zip(spectrum_arr, voltage_led_arr)]



    #print("bin_data: ", bin_data(led_55))
    sadsdf = np.array([bin_data(led_55)[0],
                       np.arange(bin_data(led_55)[1].size -1)])
    #print(get_mean_poisson(sadsdf, kind="discrete"))
    # TODO diskrete poisson verteilung aus den messreihen aufstellen und daraus die mittelwerte vom poisson bestimmen.

    #Fr.graph(*gate_8, title=r"Histogramm bei einem Gate von $8ns$ $(LI =3,00;U_{bias} = 58V$)", xlabel="ADC Counts", ylabel="ADC Channel", marker=".")
    #Fr.graph(*gate_7000, title=r"Histogramm bei einem Gate von $7000ns$ $(LI =3,00;U_{bias} = 58V$)", xlabel="ADC Counts", ylabel="ADC Channel", marker=".")

    lam1 = [0.8490179245983765,
            0.9796045545775096,
            1.0686742822483615,
            1.1139947941398765,
            1.145588234468689,
            1.1401587166206688,
            1.0992519735912027,
            1.0840128415199013]


    #fit_55 = get_poisson_from_hist(led_55, p0=[lam1[0], 1])
    #fits = np.array([get_poisson_from_hist(spectrum_i, p0=[lam1_i, 1]) for spectrum_i, lam1_i in zip(spectrum_arr, lam1)])
    #print(fits)
    #plt.plot(*led_55)
    #print("dsdfdsfgsf", *[i.nominal_value for i in poisson(led_55[0], *fit_55)])
    #print("x = ", led_55[0])
    #print("params = ", poisson(led_55[0], *[i.nominal_value for i in fit_55]))
    #print(np.average(led_55[0], weights = led_55[1]))

    #Us = [57,60,63]
    #Titles = [r"Dunkelspektrum, $U_{bias} = 57, LI=0$",
    #          r"Dunkelspektrum, $U_{bias} = 60, LI=0$",
    #          r"Dunkelspektrum, $U_{bias} = 63, LI=0$"]
    #for i, u, t in zip(dunkel_arr, Us, Titles):
    #    Fr.graph(*i, title=t, xlabel="ADC Count", ylabel="ADC Channel", ylog=True, marker=".")




# DunkelSpektren
print()
print("---------------------------------------")
print("Dunkelspektren")
print()


#def f_05(spectrum):
   # """
   # [([], gain),
   #  ([], gain),
 #    ([], gain)]
 #   :param spectrum:
 #   :return:
  #  """


def f_05(spectrum):
    """
    []
    :param spectrum_s:
    :param gain:
    :return:
    """
    i0 = get_index_peak(spectrum, 0)
    gain = get_gain(spectrum)
    f_05_sum = spectrum[1, i0+int(gain.nominal_value/2):].sum()
    f_05_sum_uf = unc.ufloat(f_05_sum, np.sqrt(f_05_sum))
    f_ges_sum = spectrum[1].sum()
    f_ges_sum_uf = unc.ufloat(f_ges_sum, np.sqrt(f_ges_sum))
    f_05_ = f_05_sum_uf / f_ges_sum_uf
    return unc.ufloat(f_05_.nominal_value, 0.0012)

def f_n(spectrum, n):
    """
    []
    :param spectrum_s:
    :param gain:
    :return:
    """
    i0 = get_index_peak(spectrum, 0)
    gain = get_gain(spectrum)
    f_n_sum = spectrum[1, i0+int(gain.nominal_value*n):].sum()
    f_n_sum_uf = unc.ufloat(f_n_sum, np.sqrt(f_n_sum))
    f_ges_sum = spectrum[1].sum()
    f_ges_sum_uf = unc.ufloat(f_ges_sum, np.sqrt(f_ges_sum))
    f_n_ = f_n_sum_uf / f_ges_sum_uf
    return unc.ufloat(f_n_.nominal_value, 0.0012)

def DCR(_f_05, tau_gat):
    return _f_05 / tau_gat

def cn(_f_05, _f_15):
    return _f_15 / _f_05

Dunkelspektrum = False
if Dunkelspektrum:
    tau_gate =unc.ufloat(104e-9, 1e-9)
    f_05_57 = f_n(dunkel_57, 0.5)
    f_05_60 = f_n(dunkel_60, 0.5)
    f_05_63 = f_n(dunkel_63, 0.5)
    print("f_05_57 = ", f_05_57, "  DCR_05_57= ", DCR(f_05_57, tau_gate))
    print("f_05_60 = ", f_05_60, "  DCR_05_60= ", DCR(f_05_60, tau_gate))
    print("f_05_63 = ", f_05_63, "  DCR_05_63= ", DCR(f_05_63, tau_gate))
    f_15_57 = f_n(dunkel_57, 1.5)
    f_15_60 = f_n(dunkel_60, 1.5)
    f_15_63 = f_n(dunkel_63, 1.5)
    print("f_15_57 = ", f_15_57)
    print("f_15_60 = ", f_15_60)
    print("f_15_63 = ", f_15_63)

    print("CN_57 = ", cn(f_05_57, f_15_57))
    print("CN_60 = ", cn(f_05_60, f_15_60))
    print("CN_63 = ", cn(f_05_63, f_15_63))

    print("DCR_57 über angenommenen Poisson: ", DCR(get_mean_poisson(dunkel_57), tau_gate))
    print("DCR_60 über angenommenen Poisson: ", DCR(get_mean_poisson(dunkel_60), tau_gate))
    print("DCR_63 über angenommenen Poisson: ", DCR(get_mean_poisson(dunkel_63), tau_gate))


# led-model
print()
print("---------------------------------------")
print("LED-Model")
print()

def sigma_k(k, sig_0, sig_1):
    #print("sigma_0 = ", sig_0)
    #print("sigma_1 = ", sig_1)
    return np.sqrt(sig_0**2 + k*sig_1**2)

def g(x, lam, sigma_0, sigma_1, G):
    k = np.arange(10)

    def g_single(_x, _lam, _sigma_0, _sigma_1, _G, _k):
        sig_k = sigma_k(_k, _sigma_0, _sigma_1)
        a = _lam**_k/sp.special.factorial(_k) * np.exp(-_lam)
        b = 1 / (_G * sig_k * np.sqrt(2 * np.pi))
        c = np.exp(-0.5 * ((_x - _G*_k) / (_G*sig_k))**2)
        #Fr.graph(x, a*b*c)
        return a*b*c
    total_expr = np.array([g_single(x, lam, sigma_0, sigma_1, G, ki) for ki in k])
    return total_expr.sum(0)

def plot_g(spectrum, volt=None):
    lam = get_mean_poisson(spectrum).nominal_value
    sig_0 = gauss_fit(*get_cutout_of_peak(spectrum, 0))

    # inital params for sig_1
    init = [i.nominal_value for i in sig_0]
    init[0] = get_index_peak(spectrum, 1)
    #sig_1 = gauss_fit(*get_cutout_of_peak(spectrum, 1), p0=init)[1].nominal_value / 200
    #sig_0 = sig_0[1].nominal_value

    # geratene sigmas
    sig_0 = 0.07
    sig_1 = 0.06

    print("sig_0 : ",sig_0)
    print("sig_1 : ",sig_1)

    gain = get_gain(spectrum).nominal_value
    y_data = g(spectrum[0], lam, sig_0, sig_1, gain)
    y_data[y_data*1e6 < 1] = 0
    plots = ((spectrum[1], rf"Measurements", 'scatter', '.', 1),
             (y_data*1e6, rf"LED-Modell, $\sigma_0 = {sig_0}$, $\sigma_1 = {sig_1}$, $\lambda = {lam:0.2g}$, $G = {gain:0.2g}$", 'plot', None,1))
    Fr.graph(spectrum[0], plots, title=rf"LED-Modell auf Daten für Spektrum bei $U={volt}V$", ylog=True)

    #('y_data', 'label', 'plot_type {'scatter', 'plot', 'errorbar', etc.}', 'marker', 'linewidth(s)', 'y_err')


def chi(f, _x, _y, _err):
    _Y = f(_x)
    _x = (_y-_Y)/_err
    return np.sum(_x**2)

def chi_per_f(f, x, y, y_err):
    return chi(f, x, y, y_err) / x.size

def chi_value_g(spectrum, sig_0, sig_1):
    # estimated parameters
    lam = get_mean_poisson(spectrum).nominal_value
    gain = get_gain(spectrum).nominal_value

    def model(x):
        return g(x, lam, sig_0, sig_1, gain)

    y_err = np.sqrt(spectrum[1])
    y_err[y_err == 0] = 1
    return chi_per_f(model, *spectrum, y_err)

def lin_solve_zero(y, m, b):
    return (y-b)/m


LED_Modell = False
if LED_Modell:
    #                   sig_0,sig_1
    sigmas = np.array([(0.17, 0.1),  # 55
                       (0.14, 0.07), # 56
                       (0.12, 0.06), # 57
                       (0.11,0.05), # 58
                       (0.10,0.04), # 59
                       (0.09,0.04), # 60
                       (0.08,0.05), # 61
                       (0.07,0.06)]) # 62

    x2s = [chi_value_g(spectrum_i, *sigmas_i) for spectrum_i, sigmas_i in zip(spectrum_arr, sigmas)]
    #x2s = chi_value_g(spectrum_arr[0], *sigmas[0])
    print("x2s: ", x2s)

    # Berechnung Durchbruchssapnnung (auch mit propagation onlinerechner durchgeführt)
    m = unc.ufloat(19.90646415516927,0.8865067123350835)
    b = unc.ufloat(-1029.737130851791,51.728403869994736)
    print("Durchbruchsspannung = ", lin_solve_zero(0, m ,b))

    #plot_g(led_62, "62")





