# pylint: disable=missing-docstring, too-many-arguments, too-many-positional-arguments, unused-argument

from __future__ import annotations

import hydpy
import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source.typing_ import *


@pytest.mark.integration_test
def test_raster_element_level(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    hp2: hydpy.HydPy,
    regionaliser_fc_2m: hydpy_mpr.RasterRegionaliser,
    element_transformer_fc: hydpy_mpr.ElementIdentityTransformer[Any],
    gridcalibrator: type[hydpy_mpr.GridCalibrator],
) -> None:

    g = gridcalibrator(nmb_nodes=3)

    hydpy_mpr.MPR(
        mprpath=dirpath_mpr_data,
        hp=hp2,
        tasks=[
            hydpy_mpr.RasterElementTask(
                regionaliser=regionaliser_fc_2m,
                upscaler=hydpy_mpr.RasterElementDefaultUpscaler(),
                transformers=[element_transformer_fc],
            )
        ],
        calibrator=g,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert len(tuple(g.gridpoints)) == 27
    assert g.nmb_steps == 28
    assert g.likelihood == pytest.approx(0.8122366228601621)
    assert g.values == pytest.approx([5.0, 0.5, -5.0])
    fc = hp2.elements["land_dill_assl"].model.parameters.control.fc.values
    assert numpy.min(fc) == numpy.max(fc) == pytest.approx(259.0249554316203)


@pytest.mark.integration_test
def test_raster_subunit_level(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    hp2: hydpy.HydPy,
    regionaliser_fc_2m: hydpy_mpr.RasterRegionaliser,
    subunit_transformer_fc: hydpy_mpr.SubunitIdentityTransformer[Any],
    gridcalibrator: type[hydpy_mpr.GridCalibrator],
) -> None:

    g = gridcalibrator(nmb_nodes=3)

    hydpy_mpr.MPR(
        mprpath=dirpath_mpr_data,
        hp=hp2,
        tasks=[
            hydpy_mpr.RasterSubunitTask(
                regionaliser=regionaliser_fc_2m,
                upscaler=hydpy_mpr.RasterSubunitDefaultUpscaler(),
                transformers=[subunit_transformer_fc],
            )
        ],
        calibrator=g,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert len(tuple(g.gridpoints)) == 27
    assert g.nmb_steps == 28
    assert g.likelihood == pytest.approx(0.8165275073538124)
    assert g.values == pytest.approx([5.0, 0.5, -5.0])
    fc = hp2.elements["land_dill_assl"].model.parameters.control.fc.values
    assert numpy.min(fc[:4]) == numpy.max(fc[:4]) == pytest.approx(278.0)
    assert fc[4:-6] == pytest.approx([264.1511917114258, 248.77248287200928])
    assert numpy.min(fc[-6:]) == numpy.max(fc[-6:]) == pytest.approx(278.0)


@pytest.mark.integration_test
def test_raster_subunit_level_preprocessing(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    hp2: hydpy.HydPy,
    preprocessors_fc_flexible: list[hydpy_mpr.RasterPreprocessor],
    regionaliser_fc_flexible: hydpy_mpr.RasterRegionaliser,
    subunit_transformer_fc: hydpy_mpr.SubunitIdentityTransformer[Any],
    gridcalibrator: type[hydpy_mpr.GridCalibrator],
) -> None:

    g = gridcalibrator(nmb_nodes=3)

    hydpy_mpr.MPR(
        mprpath=dirpath_mpr_data,
        hp=hp2,
        preprocessors=preprocessors_fc_flexible,
        tasks=[
            hydpy_mpr.RasterSubunitTask(
                regionaliser=regionaliser_fc_flexible,
                upscaler=hydpy_mpr.RasterSubunitDefaultUpscaler(),
                transformers=[subunit_transformer_fc],
            )
        ],
        calibrator=g,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert len(tuple(g.gridpoints)) == 27
    assert g.nmb_steps == 28
    assert g.likelihood == pytest.approx(0.8144729720191278)
    assert g.values == pytest.approx([5.0, 0.5, 0.0])
    fc = hp2.elements["land_dill_assl"].model.parameters.control.fc.values
    assert numpy.min(fc[:4]) == numpy.max(fc[:4]) == pytest.approx(278.0)
    assert fc[4:-6] == pytest.approx([199.29243564605713, 392.42313385009766])
    assert numpy.min(fc[-6:]) == numpy.max(fc[-6:]) == pytest.approx(278.0)


@pytest.mark.integration_test
def test_raster_element_level_subregionalisers(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    hp2: hydpy.HydPy,
    subregionaliser_ks_2m: hydpy_mpr.RasterSubregionaliser,
    regionaliser_percmax_2m: hydpy_mpr.RasterRegionaliser,
    regionaliser_k_2m: hydpy_mpr.RasterRegionaliser,
    element_transformers_percmax: hydpy_mpr.ElementIdentityTransformer[Any],
    element_transformers_k: hydpy_mpr.ElementIdentityTransformer[Any],
    gridcalibrator: type[hydpy_mpr.GridCalibrator],
) -> None:

    g = gridcalibrator(nmb_nodes=1)

    hydpy_mpr.MPR(
        mprpath=dirpath_mpr_data,
        hp=hp2,
        subregionalisers=[subregionaliser_ks_2m],
        tasks=[
            hydpy_mpr.RasterElementTask(
                regionaliser=regionaliser_percmax_2m,
                upscaler=hydpy_mpr.RasterElementDefaultUpscaler(),
                transformers=[element_transformers_percmax],
            ),
            hydpy_mpr.RasterElementTask(
                regionaliser=regionaliser_k_2m,
                upscaler=hydpy_mpr.RasterElementDefaultUpscaler(),
                transformers=[element_transformers_k],
            ),
        ],
        calibrator=g,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert len(tuple(g.gridpoints)) == 1
    assert g.nmb_steps == 2
    assert g.likelihood == pytest.approx(0.5826522238266516)
    assert {c.name: c.value for c in g.coefficients} == {
        "k_const": 0.05,
        "k_factor_dh": 0.0005,
        "k_factor_ks": 0.05,
        "ks_factor": 5.05,
        "ks_factor_clay": 0.05,
        "ks_factor_sand": 0.05,
        "percmax_factor_ks": 5.05,
    }

    control = hp2.elements["land_dill_assl"].model.parameters.control
    assert control.percmax.value == pytest.approx(23.105109819742168)
    assert control.k.value == pytest.approx(0.4836022341103063)
