cimport cython
from libc.math cimport fabs

import numpy as np
cimport numpy as np

cdef double phi(double t) nogil:
    cdef double abs_t = fabs(t)
    if abs_t < 1:
        return 4 - 6*abs_t**2 + 3*abs_t**3
    elif abs_t < 2:
        return (2 - abs_t)**3
    else:
        return 0
       
cpdef double intp(double x, double x_low, double x_high, double dx,
                  np.ndarray[np.float64_t, ndim=1] coef,
                  np.ndarray[np.float64_t, ndim=1] extr_coef) except *:
    if (x < x_low):
        return extr_coef[0] + extr_coef[1] * (x - x_low) + extr_coef[2]* (x - x_low) ** 2 + extr_coef[3]* (x - x_low) ** 3
    elif (x > x_high):
        return extr_coef[4] + extr_coef[5] * (x - x_high) + extr_coef[6]* (x - x_high) ** 2 + extr_coef[7]* (x - x_high) ** 3

    cdef double tmp = (x - x_low) / dx
    cdef int idxl = <int>(tmp)-1
    cdef int idxh = <int>(tmp+2)
    cdef double res = 0
    cdef int k       
    for k in range(idxl, idxh+1):
        res += coef[k+1]*phi(tmp - k)
    return res

cpdef np.ndarray[np.float64_t, ndim=1] intp_array(np.ndarray[np.float64_t, ndim=1] x, double x_low,
                                                  double x_high, double dx,
                                                  np.ndarray[np.float64_t, ndim=1] coef,
                                                  np.ndarray[np.float64_t, ndim=1] extr_coef):
    cdef int i
    cdef int n = x.shape[0]
    cdef np.ndarray[np.float64_t, ndim=1] res = np.empty(n, dtype=np.float64)
    for i in range(n):
        res[i] = intp(x[i], x_low, x_high, dx, coef, extr_coef)
    return res


cpdef complex intp_cplx(double x, double x_low, double x_high, double dx,
                        np.ndarray[np.complex128_t, ndim=1] coef,
                        np.ndarray[np.complex128_t, ndim=1] extr_coef) except *:
    if (x < x_low):
        return extr_coef[0] + extr_coef[1] * (x - x_low) + extr_coef[2]* (x - x_low) ** 2 + extr_coef[3]* (x - x_low) ** 3
    elif (x > x_high):
        return extr_coef[4] + extr_coef[5] * (x - x_high) + extr_coef[6]* (x - x_high) ** 2 + extr_coef[7]* (x - x_high) ** 3

    cdef double tmp = (x - x_low) / dx
    cdef int idxl = <int>(tmp)-1
    cdef int idxh = <int>(tmp+2)
    cdef complex res = 0
    cdef int k
    for k in range(idxl, idxh+1):
        res += coef[k+1]*phi(tmp - k)
    return res

cpdef np.ndarray[np.complex128_t, ndim=1] intp_cplx_array(np.ndarray[np.float64_t, ndim=1] x, double x_low,
                                                          double x_high, double dx,
                                                          np.ndarray[np.complex128_t, ndim=1] coef,
                                                          np.ndarray[np.complex128_t, ndim=1] extr_coef):
    cdef int i
    cdef int n = x.shape[0]
    cdef np.ndarray[np.complex128_t, ndim=1] res = np.empty(n, dtype=np.complex128)
    for i in range(n):
        res[i] = intp_cplx(x[i], x_low, x_high, dx, coef, extr_coef)
    return res