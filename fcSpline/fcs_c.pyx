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
       
cpdef double intp(double x, double x_low, double dx, np.ndarray[np.float64_t, ndim=1] coef) except *:
    cdef double tmp = (x - x_low) / dx
    if (tmp < 0) or (tmp > (coef.shape[0]-4)):
        raise ValueError('x value {} out of bounds'.format(x))

    cdef int idxl = <int>(tmp)-1
    cdef int idxh = <int>(tmp+2)
    cdef double res = 0
    cdef int k       
    for k in range(idxl, idxh+1):
        res += coef[k+1]*phi(tmp - k)
    return res

cpdef np.ndarray[np.float64_t, ndim=1] intp_array(np.ndarray[np.float64_t, ndim=1] x, double x_low, double dx,
                                                  np.ndarray[np.float64_t, ndim=1] coef):
    cdef int i
    cdef int n = x.shape[0]
    cdef np.ndarray[np.float64_t, ndim=1] res = np.empty(n, dtype=np.float64)
    for i in range(n):
        res[i] = intp(x[i], x_low, dx, coef)
    return res


cpdef complex intp_cplx(double x, double x_low, double dx, np.ndarray[np.complex128_t, ndim=1] coef) except *:
    cdef double tmp = (x - x_low) / dx
    if (tmp < 0) or (tmp > (coef.shape[0]-4)):
        raise ValueError('x value {} out of bounds'.format(x))

    cdef int idxl = <int>(tmp)-1
    cdef int idxh = <int>(tmp+2)
    cdef complex res = 0
    cdef int k
    for k in range(idxl, idxh+1):
        res += coef[k+1]*phi(tmp - k)
    return res

cpdef np.ndarray[np.complex128_t, ndim=1] intp_cplx_array(np.ndarray[np.float64_t, ndim=1] x, double x_low, double dx,
                                                          np.ndarray[np.complex128_t, ndim=1] coef):
    cdef int i
    cdef int n = x.shape[0]
    cdef np.ndarray[np.complex128_t, ndim=1] res = np.empty(n, dtype=np.complex128)
    for i in range(n):
        res[i] = intp_cplx(x[i], x_low, dx, coef)
    return res