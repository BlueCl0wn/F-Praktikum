import numpy as np
import scipy as sp
from uncertainties import unumpy as unp
import uncertainties as unc



I = 5


#def mean(l: list) -> int:
#    return sum(l) / len(l)


#def list_varianz2(l: list) -> list:
#    return [(i - mean(l)) ** 2 for i in l]

#def list_varianz(l : np.ndarray) -> np.ndarray:
#    return (l - l.mean())**2

#def sum_varianz(x):
#   return sum(list_varianz(x))


def get_xx(x) -> int:
    xx = 0
    for i in range(len(x)):
        xx += x[i] ** 2
    return xx


def get_xy(x: list, y: list) -> int:
    xy = 0
    for i in range(len(x)):
        # if (x[i] is not None) & (y[i] is not None): # Attempt at making it None-Proof
        xy += x[i] * y[i]
    return xy


def sum_d_i2(x, y):
    b = get_b(x, y)
    a = get_a(x, y)

    d = 0
    for i in range(len(x)):
        d += (y[i] - b * x[i] - a) ** 2
    return d


#def get_s_x(x: np.ndarray) -> float:
#    return x.std()
#    #return math.sqrt(1 / (len(x) * (len(x) - 1)) * sum_varianz(x))


def get_b(x: np.ndarray, y: np.ndarray) -> float:
    xy = get_xy(x, y)
    xx = get_xx(x)
    return (xy - len(x) * x.mean() * y.mean()) / (xx - len(x) * x.mean() ** 2)


def get_a(x, y):
    return y.mean() - get_b(x, y) * x.mean()


def get_s_b(x, y):
    if len(x) <= 2:
        return 9999999999999
    else:
        s = (1 / (len(x) - 2)) * ((sum_d_i2(x, y)) / (x.var())) # sum_varianz(x)))
        return math.sqrt(s)


def get_s_a(x, y):
    if len(x) <= 2:
        return 9999999999999
    else:
        xx = get_xx(x)
        s = xx / len(x) * get_s_b(x, y) ** 2
        return math.sqrt(s)


def wert_x(x: np.ndarray, name: str = None) -> tuple:
    x_mean = x.mean()
    s_x_mean = x.std() # get_s_x(x)
    perc = s_x_mean / x_mean if x_mean != 0 else "Divison by Zero in method 'wert_x'."
    if name is not None:
        print(f"{name: .3e}_mean = {x_mean: .3e} +- {s_x_mean: .3e}    (+- {perc: .3e})")
        print()
    return x_mean, s_x_mean

"""
def wert_xy(x: list | np.ndarray, y: np.ndarray, y_error=None, name: str = None) -> tuple:
    # Convert to np.ndrarray if not already so.
    if type(x) == list:
        x = np.array(x)
    if type(y) == list:
        y = np.array(y)

    # Remove all None entries from the given data
    pos1 = x == None  # '==' is correct. Is would check if array is None not whether elements of array are None.
    pos2 = y == None
    pos = np.logical_or(pos1, pos2)
    x = x[~pos]
    y = y[~pos]

    params = poly_fit(x, y, deg=1, y_error=y_error)
    print("lin_fit: ", params)

    # do calcultions
    b = get_b(x, y)
    s_b = get_s_b(x, y)
    b_perc = s_b / b if b != 0 else "Divison by Zero in method 'wert_xy'."

    a = get_a(x, y)
    s_a = get_s_a(x, y)
    a_perc = s_a / a if a != 0 else "Divison by Zero in method 'wert_xy'."

    if name is not None:
        print(f"{name}:")
        print(f" -  b/m= {b: .3e} +- {s_b: .3e}  (+- {b_perc: .3e})")
        print(f" -  a/b = {a: .3e} +- {s_a: .3e}  (+- {a_perc: .3e})")
        print()

    return b, a, s_b, s_a
"""
"""
def get_trendlinie(x: list, y: list):
    """

    :param x:
    :param y:
    :return:
    """
    params = poly_fit(x, y, unc=False, func=True)[0]
    return params(x) # TODO x-Werte ändern zu np.linspace(x.min(), x.max(), x.size*100) ?

    # = np.polyfit(x, y, 1)
    #p = np.poly1d(z)
    #return p(x)
"""