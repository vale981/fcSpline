import sys
import pathlib

__fcs_module_path__ = pathlib.Path(__file__).absolute().parent.parent
sys.path.append(str(__fcs_module_path__))

import numpy as np
import fcSpline

def catch_exception(func, args, exc):
    try:
        func(*args)
    except exc as e:
        print("OK, caught", exc, e)
    except:
        raise
    else:
        assert False, "no Exception was raised but expected {}".format(exc)

def _calls_helper(y):
    xl = 1
    xh = 5

    try:
        fcSpline.FCS(xl, xh, y, ord_bound_apprx=4)
    except ValueError as e:
        print("OK: caught ValueError", e)
    else:
        assert False

    for ord_bound_apprx in [1,2,3]:
        for pp in [True, False]:
            spl = fcSpline.FCS(xl, xh, y, ord_bound_apprx=ord_bound_apprx, use_pure_python=pp)
            spl(xl)
            spl(xh)
            spl((xl+xh)/2)

            catch_exception(spl, (xl - 0.001,), ValueError)
            catch_exception(spl, (xh + 0.001,), ValueError)

            xfine = np.linspace(xl, xh, 3*(len(y)-1) + 1)
            spl(xfine)

            xfine = np.linspace(xl - 0.001, xh, 5)
            catch_exception(spl, (xfine,), ValueError)
            xfine = np.linspace(xl, xh+0.001, 5)
            catch_exception(spl, (xfine,), ValueError)

def test_calls():
    # real data
    y = [1,3,2,6,5,8]
    _calls_helper(y)

    # complex data
    y = np.asarray(y)
    y = y + 1j*y[::-1]
    _calls_helper(y)

def second_deriv(y, dx):
    return np.gradient(np.gradient(y, dx), dx)[2:-2]

def test_spline_property():
    xl = 0
    xh = 10
    n = 15
    x = np.linspace(xl, xh, n)
    y = np.sin(x)

    spl = fcSpline.FCS(xl, xh, y)

    # here we check that the spline evaluates exactly to the data points
    for i, xi in enumerate(x):
        d = abs(spl(xi) - y[i])
        assert d < 1e-14, "d={} < 1e-14 failed".format(d)

    # here we check the continuity of the second derivatives
    for fac in [3,5,7]:
        xf, dx = np.linspace(xl, xh, 500, retstep=True)
        yf = spl(xf)
        y_pp = second_deriv(yf, dx)
        d = np.abs(y_pp[1:] - y_pp[:-1])
        d1 = np.max(d)

        xf, dx = np.linspace(xl, xh, fac*500, retstep=True)
        yf = spl(xf)
        y_pp = second_deriv(yf, dx)
        d = np.abs(y_pp[1:] - y_pp[:-1])
        d2 = np.max(d)
        assert abs(fac - d1 / d2) < 0.02

    # here we check convergence for complex function
    xl = 0
    xh = 10

    n = 2**(np.asarray([6,8,10,12]))
    mrd = [5e-5, 5e-8, 6e-11, 3e-13]

    for i, ni in enumerate(n):
        x = np.linspace(xl, xh, ni)
        f = lambda x: np.sin(x) + 1j*np.exp(-(x-5)**2/10)
        y = f(x)

        spl = fcSpline.FCS(xl, xh, y)
        xf = np.linspace(xl, xh, 4*(ni-1)+1)
        yf = spl(xf)
        rd = np.abs(f(xf) - yf)/np.abs(f(xf))
        assert np.max(rd) < mrd[i]

if __name__ == "__main__":
    test_calls()
    test_spline_property()