import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import uncertainties as unc
import uncertainties.unumpy as unp
import tabulate as tl


def gaussian(x, mu, sigma, h=1):
    """
    Function to compute y values of a gaussian for given x values.

    :param float | np.ndarray x: X-values for which y values of gaussian are to be computed.
    :param float mu: \mu parameter of gaussian representing the mean of gaussian distribution.
    :param float sigma: \sigma parameter of gaussian representing the standard deviation of gaussian distribution.
    :param float h: Height factor of gaussian. Not standard parameter but is supposed to make standardizing redundant / not as critical.
    :return float | np.ndarray: int or array of ints containing the computed y-values of gaussian
    """
    a = h/(sigma*np.sqrt(2*np.pi))
    b = np.exp(-(x-mu)**2/(2*sigma**2))
    return a*b

def poisson(k, lam, h=1):
    """
    Function to compute y values of a poisson for given k values.

    :param int | np.ndarray k: integer k-values or array of k-values for which y values of poisson are to be computed.
    :param float lam: \lambda parameter of poisson distribution. \lambda represents mean and standard deviation of poisson distribution.
    :param float h: Height factor of gaussian. Not standard parameter but is supposed to make standardizing redundant / not as critical.
    :return float | np.ndarray: int or array of ints containing the computed y-values of poisson.
    """
    return h * lam**k / sp.special.factorial(k) * np.exp(-lam)


def lin(x, m, b):
    """
    Function to compute y values of a linear function for given x values.

    Using 'numpy.poly1d' is probably better. This method can be used with uncertainties.ufloats though.

    This function supports unc.ufloat operation. For example if one fits the parameters using 'lin_fit' and has them
    returned as ndarray[unc.ufloat] this method automatically gives errors of later computed y-values .

    :param float | np.ndarray x: X-values for which y values of linear euqation are to be computed.
    :param float m: slope parameter of linear equation.
    :param float b: y-intercept parameter of linear equation.
    :return float | np.ndarray: int or array of ints containing the computed y-values of poisson.
    """
    return m*x + b


def poly_fit(x, y, y_error=None, deg=1, return_func=False, uncert=False):
    """
    Function fitting a linear equation on a given dataset. Uses 'numpy.polyfit', cov="unscaled" in order to support input of standard deviations.
    params[0] is coefficient of highest order x term.

    :param array_like x: X values of dataset.
    :param array_like y: Y values of dataset.
    :param int deg: Degree of fitted polynomial. Standard value is deg=1.
    :param array_like y_error: Standard deviation of y values. Can be single value if all y values have same error or array_like if each y values has its own error.
    :return: tuple containing parameters. Slope on position zero and standard deviation of parameters on position one.
    :param bool return_func: Boolean to turn on returning of function instead of parameters. Into this function x values can be parsed to get the y values of the fitted polynomial. Uses 'numpy.poly1d'.
    :param bool uncert: Boolean to switch to an array of 'uncertainties.ufloat' instead of tuple (params, stds)
    :return: Depends on 'return_func' and 'uncert'. Standard output is a tuple (params, stds).
    """
    # Set default kwargs.
    #defaultKwargs = {'p0': None}
    #kwargs = {**defaultKwargs, **kwargs}

    # Handle y_errors
    if y_error is not None:
        w = 1/y_error
    else:
        w = None

    # Calculate parameters of polynomial and their standard deviations.
    popt, pcov = np.polyfit(x, y, deg=deg, w=w, cov="unscaled")
    errors = np.sqrt(np.diag(pcov))

    if return_func: # Return polynomial function
        return np.poly1d(popt)
    elif uncert: # Return parameters as unc.uarray
        params_uarr = unp.uarray(popt, errors)
        return params_uarr
    else: # Return as tuple of (parameters, std)
        return popt, errors


def gauss_fit(x, y, **kwargs) -> np.ndarray[unc.Variable] | tuple[np.ndarray[unc.Variable]]:
    """
    Function fitting a gaussian on a given dataset. Uses 'scipy.optimize.curve_fit' with own 'gaussian' method. 'absolute_sigma=True'.
    For more info on the parameters see documentation of 'gaussian'
    :param array_like x: X values of dataset.
    :param array_like y: Y values of dataset.
    :param kwargs: p0: initial guesses for , bool uncertainties: Whether to return the fit-parameters as ndarray of unc.ufloats or tuple of ndarrays.
    :return: [mu, sigma, h] tuple of unc.ufloats or tuple of arrays like (parameters, std). Depends on value for 'uncertainties' kwarg, standard is True.
    """
    defaultKwargs = {'p0': None, 'uncertainties': True}
    kwargs = {**defaultKwargs, **kwargs}

    popt, pcov = sp.optimize.curve_fit(gaussian, x, y, p0=kwargs["p0"], absolute_sigma=True)

    # Standard Deviations for fitted parameters
    p_std = np.sqrt(np.diag(pcov))

    # Calculate and print condition number of fit parameters on the fly.
    # print("condition number of the covariance matrix for fit of peak 0: ", np.linalg.cond(pcov))

    params_uarr = unp.uarray(popt, p_std)
    if kwargs['uncertainties']:
        return params_uarr
    else:
        return popt, p_std



def poisson_fit(x, y, **kwargs) -> np.ndarray[unc.Variable] | tuple[np.ndarray[unc.Variable]]:
    """
    Function fitting a poisson on a given dataset. Uses 'scipy.optimize.curve_fit' with own 'poisson' method. 'absolute_sigma=True'.
    For more info on the parameters see documentation of 'poisson'
    :param array_like x: X values of dataset.
    :param array_like y: Y values of dataset.
    :param kwargs: p0: initial guesses for , bool uncertainties: Whether to return the fit-parameters as ndarray of unc.ufloats or tuple of ndarrays.
    :return: [lam, h] tuple of unc.ufloats or tuple of arrays like (parameters, std). Depends on value for 'uncertainties' kwarg, standard is True.
    """

    defaultKwargs = {'p0': None, 'uncertainties': True}
    kwargs = {**defaultKwargs, **kwargs}

    popt, pcov = sp.optimize.curve_fit(poisson, x, y, p0=kwargs["p0"], absolute_sigma=True)

    # Standard Deviations for fitted parameters
    p_std = np.sqrt(np.diag(pcov))

    # Calculate and print condition number of fit parameters on the fly.
    # print("condition number of the covariance matrix for fit of peak 0: ", np.linalg.cond(pcov))

    if kwargs['uncertainties']:
        params_uarr = unp.uarray(popt, p_std)
        return params_uarr
    else:
        return popt, p_std


# TODO Create method for a chisquare test. Should exist in scipy, I just don't understand the functions.


def graph(x: list | np.ndarray, y: list | tuple | np.ndarray, trendlinie: bool = False, title: str = None,
          xlabel: str = None, multiple=False,
          ylabel: str = None, xlog: bool = False, ylog: bool = False, graph="scatter", marker=None, size=1, yerror=None) -> None:
    """
    Allgemeine Funktion zum Plotten von Messwerten. Kein Wundermittel, aber vereinfacht as darstellen einfacher
    Datenreihen.

    :param x: data for x-axis
    :param y: data for y-axis. Can be array_like. If there is supposed to be more than one plot in the figure,
    y can tuple of tuples of kind ('y_data', 'label', 'plot_type {'scatter', 'plot', 'errorbar', etc.}', 'marker', 'linewidth(s)', 'y_err')
    :param multiple:
    :param trendlinie: Soll automatisch eine lineare Trendlinie durch die Messwerte gelegt werden.
    Kann bisher nur lineare Funktionen fitten.
    :param title: graph title
    :param xlabel: Label for y-axis
    :param ylabel: Label for y-axis
    :param bool xlog: Determines wether the x-axis should be plotted logarithmic.
    :param ylog: Determines wether the y-axis should be plotted logarithmic.
    :param marker:
    :param graph:
    :return: None

    """
    fig, ax = plt.subplots(layout='constrained')

    # Change multple plot tuple of tuples to tuple of dicts/kwargs with support for standard values

    if (type(y) is tuple) or multiple:
        for y_i in y:
            if y_i[2] == "scatter":
                ax.scatter(x, y_i[0], linewidths=y_i[4], label=y_i[1], marker=y_i[3])
            elif y_i[2] == "plot":
                ax.plot(x, y_i[0], linewidth=y_i[4], label=y_i[1], marker=y_i[3])
            elif y_i[2] == "errorbar":
                ax.errorbar(x, y_i[0], yerr=y_i[5], linewidth=y_i[4], label=y_i[1], marker=y_i[3])
            if trendlinie:
                params, stds = poly_fit(x, y, uncert=False)
                func =  np.poly1d(params)
                ax.plot(x, func(x), color="grey", linestyle="dashed",
                        label=rf"{y_i[1]}: Trendlinie: {params[0]: .2e}$*x + {params[1]: .2e}$", marker=marker, linewidth=size)
        ax.legend()

    else:
        if graph == "scatter":
            ax.scatter(x, y, linewidths=2*size, marker=marker)
        elif graph == "plot":
            ax.plot(x, y, linewidth=1.5*size, marker=marker)
        elif graph == "errorbar":
            ax.errorbar(x, y, yerr = yerror, linewidth=1.5*size, marker=marker)
        if trendlinie:
            params, stds= poly_fit(x, y, uncert=False)
            func =  np.poly1d(params)
            ax.plot(x, func(x), color="grey", linestyle="dashed",
                    label=rf"Trendlinie: {params[0]: .2e}$*x + {params[1]: .2e}$")
            ax.legend()

    if xlog:
        ax.set_xscale("log")
    if ylog:
        ax.set_yscale("log")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid()
    plt.show()


#a = np.array([1,2,3,4,5,6,7,8,9,10])+1
#b = np.array([11,17,28,41,52,63,71,85,89,100])
#graph(a, b, trendlinie=True)


def table(data: list | tuple | np.ndarray, rowLabels: list = None, colLabels: list = None, transpose=True) -> None:
    """
    Generell function makin' some sleek lookin' tables.

    :param rowLabels: The text of the row header cells.
    :param colLabels: The text of the column header cells.
    :param data: The texts to place into the table cells.
    :param transpose: Should the data array be transposed
    :return: None
    """

    data = np.asarray(data)

    fig, ax = plt.subplots()
    if transpose:
        data = data.transpose()

    ax.table(cellText=data, rowLabels=rowLabels, colLabels=colLabels, loc='center', cellLoc='center', rowLoc='center')

    ax.axis('off')

    plt.show()


# Tabellen
def latex_table(data: list, headers: list):
    """Funktion für LaTeX Booktabs-Tabellen.

    author=gruenfink17

    :param data: table data as a list (of lists or arrays)(e.g. [x,y])
    :param headers: headers of the table as a list of strings (e.g. ["x","y"])"""
    tab = np.array(data).transpose()
    table = tl.tabulate(tab, headers=headers, tablefmt="latex_booktabs", numalign="center", stralign="center")
    return table