
cimport cython
from libc.math cimport fabs

cdef double phi(double t) nogil:
    cdef double abs_t = fabs(t)
    if abs_t < 1:
        return 4 - 6*abs_t**2 + 3*abs_t**3
    elif abs_t < 2:
        return (2 - abs_t)**3
    else:
        return 0
       
cpdef double intp(double x, double x_low, double dx, double[:] coef):
    cdef double tmp = (x - x_low) / dx
    cdef int idxl = <int>(tmp)-1
    cdef int idxh = <int>(tmp+2)
    cdef res = 0
    cdef int k       
    for k in range(idxl, idxh+1):
        res += coef[k+1]*phi(tmp - k)
    return res     
