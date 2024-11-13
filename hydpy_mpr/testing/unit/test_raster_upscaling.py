# pylint: disable=missing-docstring, unused-argument

from hydpy.models.hland import hland_control
import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import managing
from hydpy_mpr.source.typing_ import *


@pytest.mark.parametrize(
    "task_15km, expected",
    [
        (constants.UP_A, 3.0),
        (constants.UP_G, 2.2894284851066637),
        (constants.UP_H, 1.8),
        (numpy.max, 6.0),
    ],
    indirect=True,
)
def test_raster_element_default_upscaler_okay(
    task_15km: managing.RasterTask[hland_control.FC], expected: float
) -> None:
    t = task_15km
    e, u = t.equation, t.upscaler
    i = e.group.element_raster.values
    e.output[t.mask * (i == 1)] = 2.0
    assert numpy.sum(t.mask * (i == 4)) == 3
    e.output[t.mask * (i == 4)] = 1.0, 2.0, 6.0
    u.scale_up()
    assert u.id2value[int64(1)] == pytest.approx(2.0)
    assert u.id2value[int64(4)] == pytest.approx(expected)
    assert u.name2value["land_lahn_marb"] == pytest.approx(2.0)
    assert u.name2value["land_dill_assl"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "task_15km",
    [constants.UP_A, constants.UP_G, constants.UP_H, numpy.max],
    indirect=True,
)
def test_raster_element_default_upscaler_missing_id(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    t = task_15km
    e, u = t.equation, t.upscaler
    i = e.group.element_raster.values
    i[i == 1] = 2
    u.id2value[int64(1)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2value[int64(1)])
    assert numpy.isnan(u.name2value["land_lahn_marb"])


@pytest.mark.parametrize(
    "task_15km",
    [constants.UP_A, constants.UP_G, constants.UP_H, numpy.max],
    indirect=True,
)
def test_raster_element_default_upscaler_missing_value(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    t = task_15km
    e, u = t.equation, t.upscaler
    i = e.group.element_raster.values
    e.output[i == 1] = numpy.nan
    u.id2value[int64(1)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2value[int64(1)])
    assert numpy.isnan(u.name2value["land_lahn_marb"])
