from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize
import numpy

setup(
    name="fcSpline",
    author="Richard Hartmann",
    author_email="richard.hartmann@tu-dresden.de",
    url="https://github.com/cimatosa/fcSpline",
    version="0.1",
    packages=["fcSpline"],
    license="BSD (3 clause)",
    description="A fast cubic spline interpolator for real and complex data.",
    keywords=["fast", "cubic", "spline"],
    classifiers=[
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
        "Topic :: Utilities",
        "Intended Audience :: Researcher",
    ],
    platforms=["ALL"],
    setup_requires=["cython>=0.29"],
    install_requires=["numpy>=1.20", "scipy>=1.6"],
    ext_modules=cythonize(
        Extension(
            "fcSpline.fcs_c",
            ["./fcSpline/fcs_c.pyx"],
            extra_compile_args=["-O3"],
            include_dirs=[numpy.get_include()],
        )
    ),
)
