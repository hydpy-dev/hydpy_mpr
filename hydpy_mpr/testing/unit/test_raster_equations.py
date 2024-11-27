# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source.typing_ import *


def test_raster_regionaliser_fc(
    dirpath_mpr_data: DirpathMPRData, regionaliser_fc_2m: hydpy_mpr.RasterRegionaliser
) -> None:
    r = regionaliser_fc_2m
    r.apply_coefficients()
    assert numpy.nanmin(r.output) == pytest.approx(370.2333354949951)
    assert numpy.nanmean(r.output) == pytest.approx(371.63908024628955)
    assert numpy.nanmax(r.output) == pytest.approx(373.8650631904602)
    const, factor_clay, factor_density = r.coefficients
    data_clay, data_density = r.inputs.values()
    i_max = numpy.nanargmax(r.output.flatten())
    fc_max = 20.0 * (
        const.value
        + factor_clay.value * data_clay.values.flatten()[i_max]
        + factor_density.value * data_density.values.flatten()[i_max]
    )
    assert fc_max == pytest.approx(373.8650631904602)
