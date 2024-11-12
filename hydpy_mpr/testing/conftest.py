# pylint: disable=missing-docstring, redefined-outer-name

from __future__ import annotations

import os

from hydpy import pub
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source.typing_ import *
from hydpy_mpr import testing


@pytest.fixture
def dirpath_project() -> str:
    return "HydPy-H-Lahn"


@pytest.fixture
def dirpath_mpr_data(dirpath_project: str) -> str:
    return os.path.join(dirpath_project, "mpr_data")


@pytest.fixture
def filepath_feature(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, constants.FEATURE_GPKG)


@pytest.fixture
def dirpath_raster(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, constants.RASTER)


@pytest.fixture
def dirname_raster_5km() -> str:
    return "raster_5km"


@pytest.fixture
def dirname_raster_15km() -> str:
    return "raster_15km"


@pytest.fixture
def dirpath_raster_5km(dirpath_raster: str, dirname_raster_5km: str) -> str:
    return os.path.join(dirpath_raster, dirname_raster_5km)


@pytest.fixture
def dirpath_raster_15km(dirpath_raster: str, dirname_raster_15km: str) -> str:
    return os.path.join(dirpath_raster, dirname_raster_15km)


@pytest.fixture
def filepath_element_id_5km(dirpath_raster_5km: str) -> str:
    return os.path.join(dirpath_raster_5km, f"{constants.ELEMENT_ID}.tif")


@pytest.fixture
def filepath_element_id_15km(dirpath_raster_15km: str) -> str:
    return os.path.join(dirpath_raster_15km, f"{constants.ELEMENT_ID}.tif")


@pytest.fixture
def filepath_subunit_id_15km(dirpath_raster_15km: str) -> str:
    return os.path.join(dirpath_raster_15km, f"{constants.SUBUNIT_ID}.tif")


@pytest.fixture
def filename_element_sand_15km() -> str:
    return "sand_mean_0_200_res15km_%.tif"


@pytest.fixture
def filepath_element_sand(
    dirpath_raster_15km: str, filename_element_sand_15km: str
) -> str:
    return os.path.join(dirpath_raster_15km, filename_element_sand_15km)


@pytest.fixture
def dirpath_config(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, "config")


@pytest.fixture
def dirpath_experiment1(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "experiment_1.py")


@pytest.fixture
def arrange_project(dirpath_project: Literal["HydPy-H-Lahn"]) -> Iterator[None]:
    with pub.options.printprogress(False):
        reset_workingdir = testing.prepare_project(dirpath_project)
        yield
        reset_workingdir()
