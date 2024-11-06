"""This module provides utilities for preparing example data, executing tests,
simplifying docstrings, etc."""

from __future__ import annotations
import os
import shutil

import hydpy

from hydpy_mpr import data
from hydpy_mpr.testing import iotesting
from hydpy_mpr.source.typing_ import *


def get_datapath(*subdir: str) -> str:
    """Get the path to the original data path."""
    return "/".join((data.__path__[0],) + subdir)


def get_testpath(*subdir: str) -> str:
    """Get the path to the standard testing directory."""
    return "/".join((iotesting.__path__[0],) + subdir)


def prepare_project(
    projectname: Literal["HydPy-H-Lahn"], /, *, workingdir: str | None = None
) -> Callable[[], None]:
    """Prepare an example project on disk.

    >>> import os
    >>> from hydpy import repr_
    >>> from hydpy_mpr.testing import get_testpath, prepare_project

    >>> old_workingdir = os.getcwd()

    Combine HydPy's H-Lahn example project with HydPy-MPR's data.  The latter is stored
    in the `mpr_data` subdirectory.  `prepare_project` copies everything to the
    `iotesting` subpackage (by default) and automatically switches to the current
    working directory:

    >>> reset_workingdir = prepare_project("HydPy-H-Lahn")
    >>> from hydpy.core.testtools import print_filestructure
    >>> print_filestructure("HydPy-H-Lahn")  # doctest: +ELLIPSIS
    * .../hydpy_mpr/testing/iotesting/HydPy-H-Lahn
        - conditions
            - init_1996_01_01_00_00_00
                + land_dill_assl.py
                + land_lahn_kalk.py
                + land_lahn_leun.py
                + land_lahn_marb.py
                + stream_dill_assl_lahn_leun.py
                + stream_lahn_leun_lahn_kalk.py
                + stream_lahn_marb_lahn_leun.py
        - control
            - default
                + land.py
                + land_dill_assl.py
                + land_lahn_kalk.py
                + land_lahn_leun.py
                + land_lahn_marb.py
                + stream_dill_assl_lahn_leun.py
                + stream_lahn_leun_lahn_kalk.py
                + stream_lahn_marb_lahn_leun.py
        - mpr_data
            + feature.gpkg
            - raster
                - raster_1km
                    + temp.txt
                - raster_5km
                    + temp.txt
        + multiple_runs.xml
        + multiple_runs_alpha.xml
        - network
            - default
                + headwaters.py
                + nonheadwaters.py
                + streams.py
        - series
            - default
                + dill_assl_obs_q.asc
                + evap_pet_hbv96_input_normalairtemperature.nc
                + evap_pet_hbv96_input_normalevapotranspiration.nc
                + hland_96_input_p.nc
                + hland_96_input_t.nc
                + lahn_kalk_obs_q.asc
                + lahn_leun_obs_q.asc
                + lahn_marb_obs_q.asc
                + land_dill_assl_evap_pet_hbv96_input_normalairtemperature.asc
                + land_dill_assl_evap_pet_hbv96_input_normalevapotranspiration.asc
                + land_dill_assl_hland_96_input_p.asc
                + land_dill_assl_hland_96_input_t.asc
                + land_lahn_kalk_evap_pet_hbv96_input_normalairtemperature.asc
                + land_lahn_kalk_evap_pet_hbv96_input_normalevapotranspiration.asc
                + land_lahn_kalk_hland_96_input_p.asc
                + land_lahn_kalk_hland_96_input_t.asc
                + land_lahn_leun_evap_pet_hbv96_input_normalairtemperature.asc
                + land_lahn_leun_evap_pet_hbv96_input_normalevapotranspiration.asc
                + land_lahn_leun_hland_96_input_p.asc
                + land_lahn_leun_hland_96_input_t.asc
                + land_lahn_marb_evap_pet_hbv96_input_normalairtemperature.asc
                + land_lahn_marb_evap_pet_hbv96_input_normalevapotranspiration.asc
                + land_lahn_marb_hland_96_input_p.asc
                + land_lahn_marb_hland_96_input_t.asc
                + obs_q.nc
        + single_run.xml
        + single_run.xmlt

    Use the returned function `reset_workingdir` to restore the previous working
    directory:

    >>> assert repr_(os.getcwd()).endswith("/hydpy_mpr/testing/iotesting")
    >>> reset_workingdir()
    >>> assert os.getcwd() == old_workingdir

    You can copy and switch to another working directory:

    >>> reset_workingdir = prepare_project(
    ...     "HydPy-H-Lahn", workingdir=get_testpath("subdir")
    ... )
    >>> print_filestructure("HydPy-H-Lahn")  # doctest: +ELLIPSIS
    * .../hydpy_mpr/testing/iotesting/subdir/HydPy-H-Lahn
        - conditions
            ...
        + single_run.xmlt

    >>> assert repr_(os.getcwd()).endswith("/hydpy_mpr/testing/iotesting/subdir")
    >>> reset_workingdir()
    >>> assert os.getcwd() == old_workingdir
    """

    sourcedir_hydpy = os.path.join(hydpy.data.__path__[0], projectname)
    if workingdir is None:
        workingdir = get_testpath()
    targetdir_hydpy = os.path.join(workingdir, projectname)
    if os.path.exists(targetdir_hydpy):
        shutil.rmtree(targetdir_hydpy)
    shutil.copytree(sourcedir_hydpy, targetdir_hydpy)

    sourcedir_mpr = os.path.join(get_datapath(), projectname)
    targetdir_mpr = os.path.join(targetdir_hydpy, "mpr_data")
    shutil.copytree(sourcedir_mpr, targetdir_mpr)

    old_workingdir = os.path.abspath(os.getcwd())
    os.chdir(workingdir)

    def reset_workingdir() -> None:
        """Reset the current working directory to the one active before
        `prepare_project` was called."""
        os.chdir(old_workingdir)

    return reset_workingdir
