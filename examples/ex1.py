import sys
import pathlib

__fcs_module_path__ = pathlib.Path(__file__).absolute().parent.parent
sys.path.append(str(__fcs_module_path__))

print(__fcs_module_path__)

import numpy as np
import matplotlib.pyplot as plt
import fcs

n = 1400
xl = -1
xh = 2

x = np.linspace(xl, xh, n)

f = lambda x: np.sin(x)
f_pp = lambda x: -np.sin(x)
#f_pp = lambda x: 0

y = f(x)

spl = fcs.FCS(xl, xh, y, ord_bound_apprx=2)
from scipy.interpolate import InterpolatedUnivariateSpline
spl_scipy = InterpolatedUnivariateSpline(x=x, y=y, k=3)

from time import time

t_fcs = 0
t_sci = 0

x_low = spl.x_low
dx = spl.dx
coef = spl.coef

import fcs.fcs_c as fcs_c

fnc = spl.intp
fnc2 = spl.get_callable()

for x in np.random.rand(100000):
        
    t0 = time()
    fcs_value = fnc(x, x_low, dx, coef)
    #fcs_value = fnc2(x)
#    fcs_value = fcs_c.intp(x, x_low, dx, coef)
    #fcs_value = spl(x)
    
    t1 = time()
    sci_value = spl_scipy(x)
    t2 = time()
       
    t_fcs += t1 - t0
    t_sci += t2 - t1
    
print(t_fcs)
print(t_sci)
print(t_sci / t_fcs)


xfine = np.linspace(xl, xh, 500)
dx = xfine[1] - xfine[0]
yfine = [spl(xi) for xi in xfine]

#plt.plot(x, y, ls='', marker='.')
plt.plot(xfine, np.abs(f(xfine) - yfine), label='fcs')
plt.plot(xfine, np.abs(f(xfine) - spl_scipy(xfine)), label='sci')
plt.grid()
plt.yscale('log')
plt.legend()
plt.show()

# fcs_pp = np.gradient(np.gradient(yfine, [dx]), [dx])
# sci_pp = np.gradient(np.gradient(spl_scipy(xfine), [dx]), [dx])
# 
# plt.plot(xfine, fcs_pp)
# plt.plot(xfine, sci_pp)
# plt.plot(xfine, f_pp(xfine))
# 
# plt.grid()
# plt.show()
