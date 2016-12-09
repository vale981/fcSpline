import numpy as np
from scipy.linalg import solve_banded
import traceback
import warnings

try:
    from . import fcs_c
    has_fcs_s = True
except ImportError:
    warnings.warn("could not import cython extension 'fcs_c' -> use pure Python variant")
    traceback.print_exc()
    has_fcs_s = False
    
from functools import partial

    
def _phi(t):
    abs_t = abs(t)
    if abs_t < 1:
        return 4 - 6*abs_t**2 + 3*abs_t**3
    elif abs_t < 2:
        return (2 - abs_t)**3
    else:
        return 0

def _intp(x, x_low, x_high, dx, coef, extr_coef):
    if (x < x_low):
        return extr_coef[0] + extr_coef[1] * (x - x_low) + extr_coef[2]* (x - x_low) ** 2 + extr_coef[3]* (x - x_low) ** 3
    elif (x > x_high):
        return extr_coef[4] + extr_coef[5] * (x - x_high) + extr_coef[6]* (x - x_high) ** 2 + extr_coef[7]* (x - x_high) ** 3

    tmp = (x - x_low) / dx
    idxl = int(tmp)-1
    idxh = int(tmp+2)

    #assert FCS._phi(tmp - (idxl - 1)) == 0
    #assert FCS._phi(tmp - (idxh + 1)) == 0
    
    res = 0        
    for k in range(idxl, idxh+1):
        res += coef[k+1]*_phi(tmp - k)
    return res

def _intp_array(x, x_low, x_high, dx, coef, extr_coef):
    res = np.empty(shape=x.shape, dtype=coef.dtype)
    for i, xi in enumerate(x):
        res[i] = _intp(xi, x_low, x_high, dx, coef, extr_coef)
    return res
    

# check https://en.wikipedia.org/wiki/Finite_difference_coefficient#Forward_and_backward_finite_difference
def snd_finite_diff_1(y, dx, forward=True):
    if not forward:
        y = y[::-1]
    return (y[0] - 2*y[1] + y[2]) / dx**2

def snd_finite_diff_2(y, dx, forward=True):
    if not forward:
        y = y[::-1]
    return (2*y[0] - 5*y[1] + 4*y[2]-y[3]) / dx**2

def snd_finite_diff_3(y, dx, forward=True):
    if not forward:
        y = y[::-1]
    return (35/12*y[0] - 26/3*y[1] + 19/2*y[2] - 14/3*y[3]+11/12*y[4]) / dx**2
    

class FCS(object):
    def __init__(self, x_low, x_high, y, ord_bound_apprx=3, use_pure_python = False):
        if x_high <= x_low:
            raise ValueError("x_high must be greater that x_low")
        self.x_low = x_low
        self.x_high = x_high
        
        if not isinstance(y, np.ndarray):
            y = np.asarray(y)
        if y.ndim > 1:
            raise ValueError("y must be 1D")
        self.y = y
        self.n = len(y)
        self.dx = (x_high - x_low) / (self.n-1)
        if np.iscomplexobj(self.y):
            self.dtype = np.complex128
        else:
            self.dtype = np.float64
        
        if ord_bound_apprx == 1:
            snd_finite_diff = snd_finite_diff_1
        elif ord_bound_apprx == 2:
            snd_finite_diff = snd_finite_diff_2
        elif ord_bound_apprx == 3:
            snd_finite_diff = snd_finite_diff_3
        else:
            raise ValueError("ord_bound_apprx of '{}' not implemented".format(ord_bound_apprx))
        
        self.alpha = snd_finite_diff(self.y, self.dx, forward=True)
        self.beta = snd_finite_diff(self.y, self.dx, forward=False)
        
        self.coef = self.get_coeffs()
        if has_fcs_s and not use_pure_python:
            if self.dtype == np.complex128:
                self.intp = fcs_c.intp_cplx
                self.intp_array = fcs_c.intp_cplx_array
            else:
                self.intp = fcs_c.intp
                self.intp_array = fcs_c.intp_array
        else:
            if has_fcs_s:
                warnings.warn("Note: you are using pure python, even though the c extension is avaiable!")
            self.intp = _intp
            self.intp_array = _intp_array

        self.extr_coef = np.asarray([y[0] , 3 * (self.coef[2]  - self.coef[0] ) / self.dx, self.alpha/2,
                                     (-self.coef[0] + 3 * self.coef[1] - 3 * self.coef[2] + self.coef[3]) / self.dx**3,
                                     y[-1], 3 * (self.coef[-2] - self.coef[-4]) / self.dx, self.beta/2,
                                     (-self.coef[-5] + 3*self.coef[-4]-3*self.coef[-3]+self.coef[-2]) / self.dx**3])



    def get_coeffs(self):
        coef = np.empty(shape=(self.n+2), dtype = self.dtype)
        coef[1]  = (self.y[0 ] - (self.alpha * self.dx**2)/6) / 6
        coef[-2] = (self.y[-1] - (self.beta  * self.dx**2)/6) / 6
    
        ab       = np.ones((3, self.n - 2))
        ab[1, :] = 4
        b      = self.y[1:-1].copy()
        b[0]  -= coef[1]
        b[-1] -= coef[-2]
    
        coef[2:-2] = solve_banded((1, 1), ab, b, overwrite_ab=True)
        coef[0]  = self.alpha * self.dx**2/6 + 2 * coef[1] - coef[2]
        coef[-1] = self.beta  * self.dx**2/6 + 2 * coef[-2] - coef[-3]
        
        #add dummy 0 at end
        coef = np.hstack((coef, [0]))
        
        return coef           
    
    def __call__(self, x):
        if isinstance(x, np.ndarray):
            res = np.empty(shape=x.shape, dtype=self.dtype)
            flat_res = res.flat

            flat_res[:] = self.intp_array(x.flatten(), self.x_low, self.x_high, self.dx, self.coef, self.extr_coef)

            return res
        else:
            return self.intp(x, self.x_low, self.x_high, self.dx, self.coef, self.extr_coef)

class NPointPoly(object):
    def __init__(self, x, y):
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.n = len(self.x)

    def __call__(self, x):
        C = self.y
        D = self.y
        res = self.y[0]
        for m in range(self.n-1):
            x_i      = self.x[:-(m + 1)]
            x_i_m_p1 = self.x[m + 1:]
            D_new = (x_i_m_p1 - x)*(C[1:] - D[:-1]) / (x_i - x_i_m_p1)
            C_new = (x_i - x)*(C[1:] - D[:-1]) / (x_i - x_i_m_p1)
            C = C_new
            D = D_new
            res += C_new[0]
            print()
        return res