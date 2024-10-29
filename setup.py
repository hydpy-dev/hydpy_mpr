"""Metadata of the HydPy-MPR library."""

import os

import setuptools


setuptools.setup(
    name="HydPy-MPR",
    version="0.0.dev0",
    description="Calibrate HydPy with MPR (Multiscale Parameter Regionalisation)",
    author="HydPy Developers",
    author_email="c.tyralla@bjoernsen.de",
    url="https://github.com/hydpy-dev/hydpy_mpr",
    license="LGPL-3.0",
    classifiers=[
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
    ],
    keywords="hydrology modelling water balance rainfall runoff",
    packages=(
        ["hydpy_mpr"]
        + [f"hydpy_mpr.{p}" for p in setuptools.find_namespace_packages("hydpy_mpr")]
    ),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "click",
        "coverage",
        "fudgeo",
        "geotiff",
        "hydpy",
        "imagecodecs",
        "nlopt",
        "numpy",
    ],
)
