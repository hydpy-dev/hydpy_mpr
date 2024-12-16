# pylint: disable=missing-docstring, redefined-outer-name, too-many-arguments, too-many-positional-arguments, unused-argument

from __future__ import annotations

import os
import runpy

import hydpy
from hydpy import pub
from hydpy.models.hland import hland_control
import pytest

import hydpy_mpr
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
def dirpath_mpr_data(dirpath_project: str) -> DirpathMPRData:
    return DirpathMPRData(os.path.join(dirpath_project, "mpr_data"))


@pytest.fixture
def filepath_feature(dirpath_mpr_data: DirpathMPRData) -> FilepathGeopackage:
    return FilepathGeopackage(os.path.join(dirpath_mpr_data, constants.FEATURE_GPKG))


@pytest.fixture
def name_feature_class() -> NameProvider:
    return NameProvider("LBM2018_huek250_DGMglo_Element_Subunit_DISS_MP_simply10m")


@pytest.fixture
def name_attribute_kf() -> NameDataset:
    return NameDataset("kf")


@pytest.fixture
def dirpath_raster(dirpath_mpr_data: DirpathMPRData) -> str:
    return os.path.join(dirpath_mpr_data, constants.RASTER)


@pytest.fixture
def dirname_raster_5km() -> NameProvider:
    return NameProvider("raster_5km")


@pytest.fixture
def dirname_raster_15km() -> NameProvider:
    return NameProvider("raster_15km")


@pytest.fixture
def dirpath_raster_5km(dirpath_raster: NameProvider, dirname_raster_5km: str) -> str:
    return os.path.join(dirpath_raster, dirname_raster_5km)


@pytest.fixture
def dirpath_raster_15km(dirpath_raster: str, dirname_raster_15km: NameProvider) -> str:
    return os.path.join(dirpath_raster, dirname_raster_15km)


@pytest.fixture
def filepath_element_id_5km(dirpath_raster_5km: NameProvider) -> str:
    return os.path.join(dirpath_raster_5km, f"{constants.ELEMENT_ID}.tif")


@pytest.fixture
def filepath_element_id_15km(dirpath_raster_15km: NameProvider) -> str:
    return os.path.join(dirpath_raster_15km, f"{constants.ELEMENT_ID}.tif")


@pytest.fixture
def filepath_subunit_id_15km(dirpath_raster_15km: NameProvider) -> str:
    return os.path.join(dirpath_raster_15km, f"{constants.SUBUNIT_ID}.tif")


@pytest.fixture
def filename_sand_2m_15km() -> str:
    return "sand_mean_0_200_res15km_pct.tif"


@pytest.fixture
def rastername_sand_2m_15km(filename_sand_2m_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_sand_2m_15km)


@pytest.fixture
def filepath_sand_2m_15km(dirpath_raster_15km: str, filename_sand_2m_15km: str) -> str:
    return os.path.join(dirpath_raster_15km, filename_sand_2m_15km)


@pytest.fixture
def filename_clay_1m_15km() -> str:
    return "clay_mean_0_100_res15km_pct.tif"


@pytest.fixture
def rastername_clay_1m_15km(filename_clay_1m_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_clay_1m_15km)


@pytest.fixture
def filename_clay_2m_15km() -> str:
    return "clay_mean_0_200_res15km_pct.tif"


@pytest.fixture
def rastername_clay_2m_15km(filename_clay_2m_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_clay_2m_15km)


@pytest.fixture
def filename_density_1m_15km() -> str:
    return "bdod_mean_0_100_res15km_gcm3.tif"


@pytest.fixture
def rastername_density_1m_15km(filename_density_1m_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_density_1m_15km)


@pytest.fixture
def filename_density_2m_15km() -> str:
    return "bdod_mean_0_200_res15km_gcm3.tif"


@pytest.fixture
def rastername_density_2m_15km(filename_density_2m_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_density_2m_15km)


@pytest.fixture
def filename_landuse_15km() -> str:
    return "landuse_lbm_res15km.tif"


@pytest.fixture
def rastername_landuse_15km(filename_landuse_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_landuse_15km)


@pytest.fixture
def filename_dh_15km() -> str:
    return "dh_cop_eu_dem_res15km.tif"


@pytest.fixture
def rasterfilename_dh_15km(filename_dh_15km: str) -> NameDataset:
    return hydpy_mpr.RasterGroup.extract_name_dataset(filename_dh_15km)


@pytest.fixture
def dirpath_config(dirpath_mpr_data: DirpathMPRData) -> str:
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
    dirpath_mpr_data: DirpathMPRData,
    filepath_regionalisers: str,
    dirname_raster_15km: NameProvider,
    rastername_clay_2m_15km: NameDataset,
    rastername_density_2m_15km: NameDataset,
) -> regionalising.RasterRegionaliser:

    fc = runpy.run_path(filepath_regionalisers)["FC2m"](
        source=dirname_raster_15km,
        source_clay=rastername_clay_2m_15km,
        source_density=rastername_density_2m_15km,
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
    providers = reading.RasterGroups(mprpath=dirpath_mpr_data, equations=(fc,))
    fc.activate(provider=providers[dirname_raster_15km])
    return fc


@pytest.fixture
def regionaliser_percmax_2m(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    filepath_regionalisers: str,
    dirname_raster_15km: NameProvider,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["PercMax"](
        source=dirname_raster_15km,
        source_ks="ks_2m",
        coef_factor=regionalising.Coefficient(
            name="percmax_factor_ks", default=1.0, lower=0.1, upper=10.0
        ),
    )

    assert isinstance(r, regionalising.RasterRegionaliser)
    return r


@pytest.fixture
def regionaliser_k_2m(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    filepath_regionalisers: str,
    dirname_raster_15km: NameProvider,
    filename_dh_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["K"](
        source=dirname_raster_15km,
        source_ks="ks_2m",
        source_dh=filename_dh_15km.split(".")[0],
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
    dirpath_mpr_data: DirpathMPRData,
    filepath_regionalisers: str,
    dirname_raster_15km: NameProvider,
    filename_sand_2m_15km: str,
    filename_clay_2m_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["KS"](
        name="ks_2m",
        source=dirname_raster_15km,
        source_sand=filename_sand_2m_15km.split(".")[0],
        source_clay=filename_clay_2m_15km.split(".")[0],
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
    dirpath_mpr_data: DirpathMPRData,
    filepath_regionalisers: str,
    dirname_raster_15km: NameProvider,
    filename_landuse_15km: str,
    filename_clay_2m_15km: str,
    filename_density_2m_15km: str,
) -> regionalising.RasterRegionaliser:

    r = runpy.run_path(filepath_regionalisers)["FCFlex"](
        source=dirname_raster_15km,
        source_clay="clay",
        source_density="bdod",
        source_depth="depth",
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
    dirname_raster_15km: NameProvider,
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
        source=dirname_raster_15km,
        source_1m=filename_clay_1m_15km.split(".")[0],
        source_2m=filename_clay_2m_15km.split(".")[0],
        source_landuse=filename_landuse_15km.split(".")[0],
    )
    assert isinstance(clay, preprocessing.RasterPreprocessor)

    bdod = selector(
        name="bdod",
        source=dirname_raster_15km,
        source_1m=filename_density_1m_15km.split(".")[0],
        source_2m=filename_density_2m_15km.split(".")[0],
        source_landuse=filename_landuse_15km.split(".")[0],
    )
    assert isinstance(bdod, preprocessing.RasterPreprocessor)

    depth = classes["SoilDepth"](
        name="depth",
        source=dirname_raster_15km,
        source_landuse=filename_landuse_15km.split(".")[0],
    )
    assert isinstance(depth, preprocessing.RasterPreprocessor)

    return [clay, bdod, depth]


@pytest.fixture
def element_transformer_fc() -> (
    transforming.ElementIdentityTransformer[hland_control.FC]
):
    return transforming.ElementIdentityTransformer(
        parameter=hland_control.FC, model="hland_96"
    )


@pytest.fixture
def element_transformers_percmax() -> (
    transforming.ElementIdentityTransformer[hland_control.PercMax]
):
    return transforming.ElementIdentityTransformer(
        parameter=hland_control.PercMax, model="hland_96"
    )


@pytest.fixture
def element_transformers_k() -> (
    transforming.ElementIdentityTransformer[hland_control.K]
):
    return transforming.ElementIdentityTransformer(
        parameter=hland_control.K, model="hland_96"
    )


@pytest.fixture
def subunit_transformer_fc() -> (
    transforming.SubunitIdentityTransformer[hland_control.FC]
):
    return transforming.SubunitIdentityTransformer(
        parameter=hland_control.FC, model="hland_96"
    )


@pytest.fixture
def task_raster_element(
    hp1: hydpy.HydPy,
    dirpath_mpr_data: DirpathMPRData,
    regionaliser_fc_2m: regionalising.RasterRegionaliser,
    request: pytest.FixtureRequest,
) -> managing.RasterElementTask:

    function: RasterUpscalingOption
    upscaler, function, transformer = request.param
    assert issubclass(upscaler, upscaling.RasterElementUpscaler)
    assert issubclass(transformer, transforming.ElementTransformer)

    task = managing.RasterElementTask(
        regionaliser=regionaliser_fc_2m,
        upscaler=upscaler(function=function),
        transformers=[transformer(parameter=hland_control.FC, model="hland_96")],
    )
    providers = reading.RasterGroups(
        mprpath=dirpath_mpr_data, equations=(regionaliser_fc_2m,)
    )
    task.activate(hp=hp1, provider=providers[regionaliser_fc_2m.source])
    return task


@pytest.fixture
def task_raster_subunit(
    hp1: hydpy.HydPy,
    dirpath_mpr_data: DirpathMPRData,
    regionaliser_fc_2m: regionalising.RasterRegionaliser,
    request: pytest.FixtureRequest,
) -> managing.RasterSubunitTask:

    function: RasterUpscalingOption
    upscaler, function, transformer = request.param
    assert issubclass(upscaler, upscaling.RasterSubunitUpscaler)
    assert issubclass(transformer, transforming.SubunitTransformer)

    task = managing.RasterSubunitTask(
        regionaliser=regionaliser_fc_2m,
        upscaler=upscaler(function=function),
        transformers=[transformer(parameter=hland_control.FC, model="hland_96")],
    )
    providers = reading.RasterGroups(
        mprpath=dirpath_mpr_data, equations=(regionaliser_fc_2m,)
    )
    task.activate(hp=hp1, provider=providers[regionaliser_fc_2m.source])
    return task


@pytest.fixture
def nloptcalibrator() -> calibrating.NLOptCalibrator:
    class MyCalibrator(calibrating.NLOptCalibrator):

        @override
        def calculate_likelihood(self) -> float:
            return sum(hydpy.nse(node=node) for node in self.hp.nodes) / 4.0

    return MyCalibrator(maxeval=100)


@pytest.fixture
def gridcalibrator() -> type[calibrating.GridCalibrator]:

    class TestGridCalibrator(calibrating.GridCalibrator):

        @override
        def calculate_likelihood(self) -> float:
            return sum(hydpy.nse(node=node) for node in self.hp.nodes) / 4.0

    return TestGridCalibrator


@pytest.fixture
def gridcalibrator_with_dummy_coefficients() -> type[calibrating.GridCalibrator]:

    c1 = regionalising.Coefficient(name="c1", default=1.0, lower=-1.0, upper=1.0)
    c2 = regionalising.Coefficient(name="c2", default=2.0, lower=2.0, upper=6.0)

    class TestGridCalibrator(calibrating.GridCalibrator):
        @override
        @property
        def coefficients(self) -> Sequence[regionalising.Coefficient]:
            return (c1, c2)

        @override
        def calculate_likelihood(self) -> float:
            assert False

    return TestGridCalibrator
