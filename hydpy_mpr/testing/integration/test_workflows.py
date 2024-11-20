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
    dirpath_mpr_data: str,
    hp2: hydpy.HydPy,
    regionaliser_fc_2m: hydpy_mpr.RasterRegionaliser,
    element_transformer_fc: hydpy_mpr.RasterElementIdentityTransformer[Any],
    nloptcalibrator: hydpy_mpr.NLOptCalibrator,
) -> None:

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
        calibrator=nloptcalibrator,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert nloptcalibrator.likelihood == pytest.approx(0.8110012729432962)
    assert nloptcalibrator.values == pytest.approx(
        [5.0, 0.4132740282002442, -3.215380839645377]
    )
    fc = hp2.elements["land_dill_assl"].model.parameters.control.fc.values
    assert numpy.min(fc) == numpy.max(fc) == pytest.approx(257.5034399871806)


@pytest.mark.integration_test
def test_raster_subunit_level(
    arrange_project: None,
    dirpath_mpr_data: str,
    hp2: hydpy.HydPy,
    regionaliser_fc_2m: hydpy_mpr.RasterRegionaliser,
    subunit_transformer_fc: hydpy_mpr.RasterSubunitIdentityTransformer[Any],
    nloptcalibrator: hydpy_mpr.NLOptCalibrator,
) -> None:

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
        calibrator=nloptcalibrator,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert nloptcalibrator.likelihood == pytest.approx(0.818256247212652)
    assert nloptcalibrator.values == pytest.approx(
        [5.0, 0.5267278445642123, -4.9999999999925]
    )
    fc = hp2.elements["land_dill_assl"].model.parameters.control.fc.values
    assert numpy.min(fc[:4]) == numpy.max(fc[:4]) == pytest.approx(278.0)
    assert fc[4:-6] == pytest.approx([280.47638276, 264.40416301])
    assert numpy.min(fc[-6:]) == numpy.max(fc[-6:]) == pytest.approx(278.0)


@pytest.mark.integration_test
def test_raster_subunit_level_preprocessing(
    arrange_project: None,
    dirpath_mpr_data: str,
    hp2: hydpy.HydPy,
    preprocessors_fc_flexible: list[hydpy_mpr.RasterPreprocessor],
    regionaliser_fc_flexible: hydpy_mpr.RasterRegionaliser,
    subunit_transformer_fc: hydpy_mpr.RasterSubunitIdentityTransformer[Any],
    nloptcalibrator: hydpy_mpr.NLOptCalibrator,
) -> None:

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
        calibrator=nloptcalibrator,
        writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
    ).run()

    assert nloptcalibrator.likelihood == pytest.approx(0.8154531497952633)
    assert nloptcalibrator.values == pytest.approx([26.317158773910958, 0.0, -5.0])
    fc = hp2.elements["land_dill_assl"].model.parameters.control.fc.values
    assert numpy.min(fc[:4]) == numpy.max(fc[:4]) == pytest.approx(278.0)
    assert fc[4:-6] == pytest.approx([194.3148149586912, 382.6925245001308])
    assert numpy.min(fc[-6:]) == numpy.max(fc[-6:]) == pytest.approx(278.0)
