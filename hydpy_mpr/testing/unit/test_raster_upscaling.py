# pylint: disable=missing-docstring, unused-argument

from hydpy.models.hland import hland_control
import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import managing
from hydpy_mpr.source import upscaling
from hydpy_mpr.source.typing_ import *

UpElement = upscaling.RasterElementDefaultUpscaler
UpSubunit = upscaling.RasterSubunitDefaultUpscaler


@pytest.mark.parametrize(
    "task_15km, expected",
    [
        ((UpElement, constants.UP_A), 3.0),
        ((UpElement, constants.UP_G), 2.2894284851066637),
        ((UpElement, constants.UP_H), 1.8),
        ((UpElement, numpy.max), 6.0),
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
    assert isinstance(u, UpElement)
    assert len(u.id2value) == 5
    assert u.id2value[int64(1)] == pytest.approx(2.0)
    assert u.id2value[int64(4)] == pytest.approx(expected)
    assert u.name2value["land_lahn_marb"] == pytest.approx(2.0)
    assert u.name2value["land_dill_assl"] == pytest.approx(expected)


@pytest.mark.parametrize("task_15km", [(UpElement, constants.UP_A)], indirect=True)
def test_raster_element_default_upscaler_missing_id(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    t = task_15km
    e, u = t.equation, t.upscaler
    i = e.group.element_raster.values
    i[i == 1] = 2
    assert isinstance(u, UpElement)
    u.id2value[int64(1)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2value[int64(1)])
    assert numpy.isnan(u.name2value["land_lahn_marb"])


@pytest.mark.parametrize(
    "task_15km",
    [
        (UpElement, constants.UP_A),
        (UpElement, constants.UP_G),
        (UpElement, constants.UP_H),
        (UpElement, numpy.max),
    ],
    indirect=True,
)
def test_raster_element_default_upscaler_missing_value(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    t = task_15km
    e, u = t.equation, t.upscaler
    i = e.group.element_raster.values
    e.output[i == 1] = 2.0, 2.0, 2.0, numpy.nan, 2.0, 2.0, 2.0
    assert isinstance(u, UpElement)
    u.id2value[int64(1)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2value[int64(1)])
    assert numpy.isnan(u.name2value["land_lahn_marb"])


@pytest.mark.parametrize(
    "task_15km, expected",
    [
        ((UpSubunit, constants.UP_A), 3.0),
        ((UpSubunit, constants.UP_G), 2.2894284851066637),
        ((UpSubunit, constants.UP_H), 1.8),
        ((UpSubunit, numpy.max), 6.0),
    ],
    indirect=True,
)
def test_raster_subunit_default_upscaler_okay(
    task_15km: managing.RasterTask[hland_control.FC], expected: float
) -> None:
    t = task_15km
    o, u = t.equation.output, t.upscaler
    e = t.equation.group.element_raster.values
    s = t.equation.group.subunit_raster.values
    o[t.mask * (e == 3) * (s == 0)] = 1.0, 2.0, 6.0
    u.scale_up()
    assert isinstance(u, UpSubunit)
    assert u.id2idx2value[int64(3)][int64(0)] == pytest.approx(expected)


@pytest.mark.parametrize("task_15km", [(UpSubunit, constants.UP_A)], indirect=True)
def test_raster_subunit_default_upscaler_missing_id(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    t = task_15km
    o, u = t.equation.output, t.upscaler
    e = t.equation.group.element_raster.values
    s = t.equation.group.subunit_raster.values
    s[t.mask * (e == 3) * (s == 0)] = 1
    assert isinstance(u, UpSubunit)
    u.id2idx2value[int64(3)][int64(0)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2idx2value[int64(3)][int64(0)])


@pytest.mark.parametrize(
    "task_15km",
    [
        (UpSubunit, constants.UP_A),
        (UpSubunit, constants.UP_G),
        (UpSubunit, constants.UP_H),
        (UpSubunit, numpy.max),
    ],
    indirect=True,
)
def test_raster_subunit_default_upscaler_missing_value(
    task_15km: managing.RasterTask[hland_control.FC],
) -> None:
    t = task_15km
    o, u = t.equation.output, t.upscaler
    e = t.equation.group.element_raster.values
    s = t.equation.group.subunit_raster.values
    o[t.mask * (e == 3) * (s == 0)] = 2.0, numpy.nan, 2.0
    assert isinstance(u, UpSubunit)
    assert len(u.id2idx2value) == 5
    assert len(u.id2idx2value[int64(1)]) == 4
    assert len(u.id2idx2value[int64(2)]) == 3
    u.id2idx2value[int64(3)][int64(0)] = float64(2.0)
    u.scale_up()
    assert isinstance(u, UpSubunit)
    assert numpy.isnan(u.id2idx2value[int64(3)][int64(0)])
