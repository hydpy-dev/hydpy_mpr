# pylint: disable=missing-docstring, redefined-outer-name, too-many-arguments, too-many-positional-arguments, unused-argument

from __future__ import annotations

import os
import runpy

import hydpy
from hydpy import pub
from hydpy.models.hland import hland_control
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import regionalising
from hydpy_mpr.source import reading
from hydpy_mpr.source import managing
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import transforming
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
    return "sand_mean_0_200_res15km_pct.tif"


@pytest.fixture
def filepath_element_sand(
    dirpath_raster_15km: str, filename_element_sand_15km: str
) -> str:
    return os.path.join(dirpath_raster_15km, filename_element_sand_15km)


@pytest.fixture
def filename_element_clay_15km() -> str:
    return "clay_mean_0_200_res15km_pct.tif"


@pytest.fixture
def filename_element_density_15km() -> str:
    return "bdod_mean_0_200_res15km_gcm3.tif"


@pytest.fixture
def dirpath_config(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, "config")


@pytest.fixture
def filepath_equations(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "equations.py")


@pytest.fixture
def filepath_experiment1(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "experiment_1.py")


@pytest.fixture
def arrange_project(dirpath_project: Literal["HydPy-H-Lahn"]) -> Iterator[None]:
    with pub.options.printprogress(False):
        reset_workingdir = testing.prepare_project(dirpath_project)
        yield
        reset_workingdir()


@pytest.fixture
def hp(arrange_project: None) -> hydpy.HydPy:
    hp = hydpy.HydPy("HydPy-H-Lahn")
    pub.timegrids = "1996-01-01", "1997-01-01", "1d"
    hp.prepare_network()
    hp.prepare_models()
    return hp


@pytest.fixture
def expected(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.fixture
def equation_fc(
    arrange_project: None,
    dirpath_mpr_data: str,
    filepath_equations: str,
    dirname_raster_15km: str,
    filename_element_clay_15km: str,
    filename_element_density_15km: str,
) -> regionalising.RasterEquation:
    fc = runpy.run_path(filepath_equations)["FC"](
        dir_group=dirname_raster_15km,
        file_clay=filename_element_clay_15km.split(".")[0],
        file_density=filename_element_density_15km.split(".")[0],
        coef_const=regionalising.Coefficient(name="const", default=2.0),
        coef_factor_clay=regionalising.Coefficient(name="factor_clay", default=0.5),
        coef_factor_density=regionalising.Coefficient(
            name="factor_density", default=-1.0
        ),
    )
    assert isinstance(fc, regionalising.RasterEquation)
    fc.activate(raster_groups=reading.RasterGroups(mprpath=dirpath_mpr_data))
    return fc


@pytest.fixture
def task_element(
    hp: hydpy.HydPy,
    dirpath_mpr_data: str,
    equation_fc: regionalising.RasterEquation,
    request: pytest.FixtureRequest,
) -> managing.RasterElementTask:

    function: UpscalingOption
    upscaler, function, transformer = request.param
    assert issubclass(upscaler, upscaling.RasterElementUpscaler)
    assert issubclass(transformer, transforming.RasterElementTransformer)

    task = managing.RasterElementTask(
        equation=equation_fc,
        upscaler=upscaler(function=function),
        transformers=[transformer(parameter=hland_control.FC, model="hland_96")],
    )
    task.activate(hp=hp, raster_groups=reading.RasterGroups(mprpath=dirpath_mpr_data))
    return task


@pytest.fixture
def task_subunit(
    hp: hydpy.HydPy,
    dirpath_mpr_data: str,
    equation_fc: regionalising.RasterEquation,
    request: pytest.FixtureRequest,
) -> managing.RasterSubunitTask:

    function: UpscalingOption
    upscaler, function, transformer = request.param
    assert issubclass(upscaler, upscaling.RasterSubunitUpscaler)
    assert issubclass(transformer, transforming.RasterSubunitTransformer)

    task = managing.RasterSubunitTask(
        equation=equation_fc,
        upscaler=upscaler(function=function),
        transformers=[transformer(parameter=hland_control.FC, model="hland_96")],
    )
    task.activate(hp=hp, raster_groups=reading.RasterGroups(mprpath=dirpath_mpr_data))
    return task
