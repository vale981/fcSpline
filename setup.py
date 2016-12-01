from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


setup(
    ext_modules = cythonize(Extension("fcs_c",
                                      ["./fcs/fcs_c.pyx"],
                                      #libraries=["m"],
                                      extra_compile_args=['-O3'],
                                      #extra_link_args=['-fopenmp'],
                                      ))
)