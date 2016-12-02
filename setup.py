from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy


setup(
    ext_modules = cythonize(Extension("fcSpline.fcs_c",
                                      ["./fcSpline/fcs_c.pyx"],
                                      #extra_compile_args=['-O3', '-funroll-loops', '-ffinite-math-only', '-fno-trapping-math'],
                                      extra_compile_args=['-Ofast'],
                                      #extra_compile_args=['-O2'],
                                      )),
    include_dirs=[numpy.get_include()]
)