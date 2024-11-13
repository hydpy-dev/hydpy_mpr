# pylint: disable=missing-docstring, unused-argument

from hydpy.models.hland import hland_control
import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import managing
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import transforming
from hydpy_mpr.source.typing_ import *

UpElement = upscaling.RasterElementDefaultUpscaler
UpSubunit = upscaling.RasterSubunitDefaultUpscaler
TransElement = transforming.RasterElementIdentityTransformer
TransSubunit = transforming.RasterSubunitIdentityTransformer


@pytest.mark.parametrize(
    "task_15km", [(UpElement, constants.UP_A, TransElement)], indirect=True
)
def test_raster_element_default_upscaler(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    u = task_15km.upscaler
    assert isinstance(u, UpElement)
    u.id2value[int64(3)] = float64(2.0)
    t = task_15km.transformers[0]
    t.modify_parameters()
    fc = t.hp.elements["land_lahn_kalk"].model.parameters.control["fc"].values
    assert numpy.min(fc) == numpy.max(fc) == 2.0
    u.id2value[int64(3)] = float64(numpy.nan)
    t.modify_parameters()
    assert numpy.min(fc) == numpy.max(fc) == 2.0


@pytest.mark.parametrize(
    "task_15km", [(UpSubunit, constants.UP_A, TransSubunit)], indirect=True
)
def test_raster_subunit_default_upscaler(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    u = task_15km.upscaler
    assert isinstance(u, UpSubunit)
    u.id2idx2value[int64(3)][int64(1)] = float64(2.0)
    u.id2idx2value[int64(3)][int64(3)] = float64(4.0)
    t = task_15km.transformers[0]
    t.modify_parameters()
    fc = t.hp.elements["land_lahn_kalk"].model.parameters.control["fc"].values
    assert fc[1] == 2.0
    assert fc[2] == 219.0
    assert fc[3] == 4.0
