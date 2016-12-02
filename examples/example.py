import sys
import pathlib

__fcs_module_path__ = pathlib.Path(__file__).absolute().parent.parent
sys.path.append(str(__fcs_module_path__))

import numpy as np
import matplotlib.pyplot as plt
import fcSpline

def ex1():
    n = 15
    xl = -10
    xh = 10
    f = lambda x: np.sin(x)
    x = np.linspace(xl, xh, n)
    y = f(x)
    spl = fcSpline.FCS(xl, xh, y)

    xfine, dxfine = np.linspace(xl, xh, 500, retstep=True)
    yfine = spl(xfine)

    plt.plot(x, y, ls='', marker='.', label='data set y=sin(x)')
    plt.plot(xfine, yfine, label='interpol.')


    y_pp = np.gradient(np.gradient(yfine, dxfine), dxfine)
    plt.plot(xfine, y_pp, label='2nd derv.')

    plt.grid()
    plt.legend()
    plt.show()

if __name__ == "__main__":
    ex1()