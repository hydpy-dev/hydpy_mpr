# pylint: disable=missing-docstring, redefined-outer-name, too-many-arguments, too-many-positional-arguments, unused-argument

from __future__ import annotations

import os
import runpy

import hydpy
from hydpy import pub
from hydpy.models.hland import hland_control
import pytest

from hydpy_mpr.source import calibrating
from hydpy_mpr.source import constants
from hydpy_mpr.source import managing
from hydpy_mpr.source import preprocessing
from hydpy_mpr.source import regionalising
from hydpy_mpr.source import reading
from hydpy_mpr.source import transforming
from hydpy_mpr.source import upscaling
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
def filename_sand_2m_15km() -> str:
    return "sand_mean_0_200_res15km_pct.tif"


@pytest.fixture
def filepath_sand_2m_15km(dirpath_raster_15km: str, filename_sand_2m_15km: str) -> str:
    return os.path.join(dirpath_raster_15km, filename_sand_2m_15km)


@pytest.fixture
def filename_clay_1m_15km() -> str:
    return "clay_mean_0_100_res15km_pct.tif"


@pytest.fixture
def filename_clay_2m_15km() -> str:
    return "clay_mean_0_200_res15km_pct.tif"


@pytest.fixture
def filename_density_1m_15km() -> str:
    return "bdod_mean_0_100_res15km_gcm3.tif"


@pytest.fixture
def filename_density_2m_15km() -> str:
    return "bdod_mean_0_200_res15km_gcm3.tif"


@pytest.fixture
def filename_landuse_15km() -> str:
    return "landuse_lbm_res15km.tif"


@pytest.fixture
def filename_dh_15km() -> str:
    return "dh_cop_eu_dem_res15km.tif"


@pytest.fixture
def dirpath_config(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, "config")


@pytest.fixture
def filepath_regionalisers(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "regionalisers.py")


@pytest.fixture
def filepath_preprocessors(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "preprocessors.py")


@pytest.fixture
def filepath_experiment_subunit_level(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "experiment_subunit_level.py")


@pytest.fixture
def arrange_project(dirpath_project: Literal["HydPy-H-Lahn"]) -> Iterator[None]:
    with pub.options.printprogress(False):
        reset_workingdir = testing.prepare_project(dirpath_project)
        yield
        reset_workingdir()


@pytest.fixture
def hp1(arrange_project: None) -> hydpy.HydPy:
    hp = hydpy.HydPy("HydPy-H-Lahn")
    pub.timegrids = "1996-01-01", "1997-01-01", "1d"
    hp.prepare_network()
    hp.prepare_models()
    return hp


@pytest.fixture
def hp2(hp1: hydpy.HydPy) -> hydpy.HydPy:
    hp1.load_conditions()
    hp1.prepare_inputseries()
    hp1.load_inputseries()
    hp1.prepare_nodeseries()
    hp1.load_obsseries()
    return hp1


@pytest.fixture
def expected(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.fixture
def regionaliser_fc_2m(
    arrange_project: None,
    dirpath_mpr_data: str,
    filepath_regionalisers: str,
    dirname_raster_15km: str,
    filename_clay_2m_15km: str,
    filename_density_2m_15km: str,
) -> regionalising.RasterRegionaliser:

    fc = runpy.run_path(filepath_regionalisers)["FC2m"](
        dir_group=dirname_raster_15km,
        file_clay=filename_clay_2m_15km.split(".")[0],
        file_density=filename_density_2m_15km.split(".")[0],
        coef_const=regionalising.Coefficient(
            name="fc_const", default=20.0, lower=5.0, upper=50.0
        ),
        coef_factor_clay=regionalising.Coefficient(
            name="fc_factor_clay", default=0.0, lower=0.0, upper=1.0
        ),
        coef_factor_density=regionalising.Coefficient(
            name="fc_factor_density", default=-1.0, lower=-5.0, upper=0.0
        ),
    )

    assert isinstance(fc, regionalising.RasterRegionaliser)
    fc.activate(raster_groups=reading.RasterGroups(mprpath=dirpath_mpr_data))
    return fc


@pytest.fixture
def regionaliser_percmax_2m(
    arrange_project: None,
    dirpath_mpr_data: str,
    filepath_regionalisers: str,
    dirname_raster_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["PercMax"](
        dir_group=dirname_raster_15km,
        file_ks="ks_2m",
        coef_factor=regionalising.Coefficient(
            name="percmax_factor_ks", default=1.0, lower=0.1, upper=10.0
        ),
    )

    assert isinstance(r, regionalising.RasterRegionaliser)
    return r


@pytest.fixture
def regionaliser_k_2m(
    arrange_project: None,
    dirpath_mpr_data: str,
    filepath_regionalisers: str,
    dirname_raster_15km: str,
    filename_dh_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["K"](
        dir_group=dirname_raster_15km,
        file_ks="ks_2m",
        file_dh=filename_dh_15km.split(".")[0],
        coef_const=regionalising.Coefficient(
            name="k_const", default=0.01, lower=0.0, upper=0.1
        ),
        coef_factor_ks=regionalising.Coefficient(
            name="k_factor_ks", default=0.01, lower=0.0, upper=0.1
        ),
        coef_factor_dh=regionalising.Coefficient(
            name="k_factor_dh", default=0.0001, lower=0.0, upper=0.001
        ),
    )
    assert isinstance(r, regionalising.RasterRegionaliser)
    return r


@pytest.fixture
def subregionaliser_ks_2m(
    arrange_project: None,
    dirpath_mpr_data: str,
    filepath_regionalisers: str,
    dirname_raster_15km: str,
    filename_sand_2m_15km: str,
    filename_clay_2m_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["KS"](
        name="ks_2m",
        dir_group=dirname_raster_15km,
        file_sand=filename_sand_2m_15km.split(".")[0],
        file_clay=filename_clay_2m_15km.split(".")[0],
        coef_factor=regionalising.Coefficient(
            name="ks_factor", default=1.0, lower=0.1, upper=10.0
        ),
        coef_factor_sand=regionalising.Coefficient(
            name="ks_factor_sand", default=0.01, lower=0.0, upper=0.1
        ),
        coef_factor_clay=regionalising.Coefficient(
            name="ks_factor_clay", default=0.01, lower=0.0, upper=0.1
        ),
    )

    assert isinstance(r, regionalising.RasterSubregionaliser)
    return r


@pytest.fixture
def regionaliser_fc_flexible(
    arrange_project: None,
    dirpath_mpr_data: str,
    filepath_regionalisers: str,
    dirname_raster_15km: str,
    filename_landuse_15km: str,
    filename_clay_2m_15km: str,
    filename_density_2m_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["FCFlex"](
        dir_group=dirname_raster_15km,
        file_clay="clay",
        file_density="bdod",
        file_depth="depth",
        coef_const=regionalising.Coefficient(
            name="const", default=20.0, lower=5.0, upper=50.0
        ),
        coef_factor_clay=regionalising.Coefficient(
            name="factor_clay", default=0.0, lower=0.0, upper=1.0
        ),
        coef_factor_density=regionalising.Coefficient(
            name="factor_density", default=-1.0, lower=-5.0, upper=0.0
        ),
    )

    assert isinstance(r, regionalising.RasterRegionaliser)
    return r


@pytest.fixture
def preprocessors_fc_flexible(
    arrange_project: None,
    filepath_preprocessors: str,
    dirname_raster_15km: str,
    filename_clay_1m_15km: str,
    filename_clay_2m_15km: str,
    filename_density_1m_15km: str,
    filename_density_2m_15km: str,
    filename_landuse_15km: str,
) -> list[preprocessing.RasterPreprocessor]:

    classes = runpy.run_path(filepath_preprocessors)
    selector = classes["DataSelector"]

    clay = selector(
        name="clay",
        dir_group=dirname_raster_15km,
        file_1m=filename_clay_1m_15km.split(".")[0],
        file_2m=filename_clay_2m_15km.split(".")[0],
        file_landuse=filename_landuse_15km.split(".")[0],
    )
    assert isinstance(clay, preprocessing.RasterPreprocessor)

    bdod = selector(
        name="bdod",
        dir_group=dirname_raster_15km,
        file_1m=filename_density_1m_15km.split(".")[0],
        file_2m=filename_density_2m_15km.split(".")[0],
        file_landuse=filename_landuse_15km.split(".")[0],
    )
    assert isinstance(bdod, preprocessing.RasterPreprocessor)

    depth = classes["SoilDepth"](
        name="depth",
        dir_group=dirname_raster_15km,
        file_landuse=filename_landuse_15km.split(".")[0],
    )
    assert isinstance(depth, preprocessing.RasterPreprocessor)

    return [clay, bdod, depth]


@pytest.fixture
def element_transformer_fc() -> (
    transforming.RasterElementIdentityTransformer[hland_control.FC]
):
    return transforming.RasterElementIdentityTransformer(
        parameter=hland_control.FC, model="hland_96"
    )


@pytest.fixture
def element_transformers_percmax() -> (
    transforming.RasterElementIdentityTransformer[hland_control.PercMax]
):
    return transforming.RasterElementIdentityTransformer(
        parameter=hland_control.PercMax, model="hland_96"
    )


@pytest.fixture
def element_transformers_k() -> (
    transforming.RasterElementIdentityTransformer[hland_control.K]
):
    return transforming.RasterElementIdentityTransformer(
        parameter=hland_control.K, model="hland_96"
    )


@pytest.fixture
def subunit_transformer_fc() -> (
    transforming.RasterSubunitIdentityTransformer[hland_control.FC]
):
    return transforming.RasterSubunitIdentityTransformer(
        parameter=hland_control.FC, model="hland_96"
    )


@pytest.fixture
def task_element(
    hp1: hydpy.HydPy,
    dirpath_mpr_data: str,
    regionaliser_fc_2m: regionalising.RasterRegionaliser,
    request: pytest.FixtureRequest,
) -> managing.RasterElementTask:

    function: UpscalingOption
    upscaler, function, transformer = request.param
    assert issubclass(upscaler, upscaling.RasterElementUpscaler)
    assert issubclass(transformer, transforming.RasterElementTransformer)

    task = managing.RasterElementTask(
        regionaliser=regionaliser_fc_2m,
        upscaler=upscaler(function=function),
        transformers=[transformer(parameter=hland_control.FC, model="hland_96")],
    )
    task.activate(hp=hp1, raster_groups=reading.RasterGroups(mprpath=dirpath_mpr_data))
    return task


@pytest.fixture
def task_subunit(
    hp1: hydpy.HydPy,
    dirpath_mpr_data: str,
    regionaliser_fc_2m: regionalising.RasterRegionaliser,
    request: pytest.FixtureRequest,
) -> managing.RasterSubunitTask:

    function: UpscalingOption
    upscaler, function, transformer = request.param
    assert issubclass(upscaler, upscaling.RasterSubunitUpscaler)
    assert issubclass(transformer, transforming.RasterSubunitTransformer)

    task = managing.RasterSubunitTask(
        regionaliser=regionaliser_fc_2m,
        upscaler=upscaler(function=function),
        transformers=[transformer(parameter=hland_control.FC, model="hland_96")],
    )
    task.activate(hp=hp1, raster_groups=reading.RasterGroups(mprpath=dirpath_mpr_data))
    return task


@pytest.fixture
def nloptcalibrator() -> calibrating.NLOptCalibrator:
    class MyCalibrator(calibrating.NLOptCalibrator):

        @override
        def calculate_likelihood(self) -> float:
            return sum(hydpy.nse(node=node) for node in self.hp.nodes) / 4.0

    return MyCalibrator(maxeval=100)
