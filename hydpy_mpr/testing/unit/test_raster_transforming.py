# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source import constants
from hydpy_mpr.source.typing_ import *

UpElement = hydpy_mpr.RasterElementDefaultUpscaler
UpSubunit = hydpy_mpr.RasterSubunitDefaultUpscaler
TransElement = hydpy_mpr.ElementIdentityTransformer
TransSubunit = hydpy_mpr.SubunitIdentityTransformer


@pytest.mark.parametrize(
    "task_raster_element", [(UpElement, constants.UP_A, TransElement)], indirect=True
)
def test_raster_element_default_upscaler(
    task_raster_element: hydpy_mpr.RasterElementTask,
) -> None:
    u = task_raster_element.upscaler
    assert isinstance(u, UpElement)
    u.id2value[int64(3)] = float64(2.0)
    t = task_raster_element.transformers[0]
    t.modify_parameters()
    fc = t.hp.elements["land_lahn_kalk"].model.parameters.control["fc"].values
    assert numpy.min(fc) == numpy.max(fc) == 2.0
    u.id2value[int64(3)] = float64(numpy.nan)
    t.modify_parameters()
    assert numpy.min(fc) == numpy.max(fc) == 2.0


@pytest.mark.parametrize(
    "task_raster_subunit", [(UpSubunit, constants.UP_A, TransSubunit)], indirect=True
)
def test_raster_subunit_default_upscaler(
    task_raster_subunit: hydpy_mpr.RasterElementTask,
) -> None:
    u = task_raster_subunit.upscaler
    assert isinstance(u, UpSubunit)
    u.id2idx2value[int64(3)][int64(1)] = float64(2.0)
    u.id2idx2value[int64(3)][int64(3)] = float64(4.0)
    t = task_raster_subunit.transformers[0]
    t.modify_parameters()
    fc = t.hp.elements["land_lahn_kalk"].model.parameters.control["fc"].values
    assert fc[1] == 2.0
    assert fc[2] == 219.0
    assert fc[3] == 4.0
