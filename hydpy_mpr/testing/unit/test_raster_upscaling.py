# pylint: disable=missing-docstring, unused-argument

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
    "task_element, expected",
    [
        ((UpElement, constants.UP_A, TransElement), 3.0),
        ((UpElement, constants.UP_G, TransElement), 2.2894284851066637),
        ((UpElement, constants.UP_H, TransElement), 1.8),
        ((UpElement, numpy.max, TransElement), 6.0),
    ],
    indirect=True,
)
def test_raster_element_default_upscaler_okay(
    task_element: managing.RasterElementTask, expected: float
) -> None:
    r = task_element.regionaliser
    u = task_element.upscaler
    i = r.group.element_raster.values
    r.output[u.mask * (i == 1)] = 2.0
    assert numpy.sum(u.mask * (i == 4)) == 3
    r.output[u.mask * (i == 4)] = 1.0, 2.0, 6.0
    u.scale_up()
    assert isinstance(u, UpElement)
    assert len(u.id2value) == 5
    assert u.id2value[int64(1)] == pytest.approx(2.0)
    assert u.id2value[int64(4)] == pytest.approx(expected)
    assert u.name2value["land_lahn_marb"] == pytest.approx(2.0)
    assert u.name2value["land_dill_assl"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "task_element", [(UpElement, constants.UP_A, TransElement)], indirect=True
)
def test_raster_element_default_upscaler_missing_id(
    task_element: managing.RasterElementTask,
) -> None:
    r = task_element.regionaliser
    u = task_element.upscaler
    i = r.group.element_raster.values
    i[i == 1] = 2
    assert isinstance(u, UpElement)
    u.id2value[int64(1)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2value[int64(1)])
    assert numpy.isnan(u.name2value["land_lahn_marb"])


@pytest.mark.parametrize(
    "task_element",
    [
        (UpElement, constants.UP_A, TransElement),
        (UpElement, constants.UP_G, TransElement),
        (UpElement, constants.UP_H, TransElement),
        (UpElement, numpy.max, TransElement),
    ],
    indirect=True,
)
def test_raster_element_default_upscaler_missing_value(
    task_element: managing.RasterElementTask,
) -> None:
    r = task_element.regionaliser
    u = task_element.upscaler
    i = r.group.element_raster.values
    r.output[i == 1] = 2.0, 2.0, 2.0, numpy.nan, 2.0, 2.0, 2.0
    assert isinstance(u, UpElement)
    u.id2value[int64(1)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2value[int64(1)])
    assert numpy.isnan(u.name2value["land_lahn_marb"])


@pytest.mark.parametrize(
    "task_subunit, expected",
    [
        ((UpSubunit, constants.UP_A, TransSubunit), 2.5),
        ((UpSubunit, constants.UP_G, TransSubunit), 2.0),
        ((UpSubunit, constants.UP_H, TransSubunit), 1.6),
        ((UpSubunit, numpy.max, TransSubunit), 4.0),
    ],
    indirect=True,
)
def test_raster_subunit_default_upscaler_okay(
    task_subunit: managing.RasterSubunitTask, expected: float
) -> None:
    u = task_subunit.upscaler
    o = task_subunit.regionaliser.output
    e = task_subunit.regionaliser.group.element_raster.values
    s = task_subunit.regionaliser.group.subunit_raster.values
    o[u.mask * (e == 3) * (s == 0)] = 1.0, 4.0
    u.scale_up()
    assert isinstance(u, UpSubunit)
    assert u.id2idx2value[int64(3)][int64(0)] == pytest.approx(expected)
    assert u.name2idx2value["land_lahn_kalk"][int64(0)] == pytest.approx(expected)


@pytest.mark.parametrize(
    "task_subunit", [(UpSubunit, constants.UP_A, TransSubunit)], indirect=True
)
def test_raster_subunit_default_upscaler_missing_id(
    task_subunit: managing.RasterSubunitTask,
) -> None:
    u = task_subunit.upscaler
    e = task_subunit.regionaliser.group.element_raster.values
    s = task_subunit.regionaliser.group.subunit_raster.values
    s[u.mask * (e == 3) * (s == 0)] = 1
    assert isinstance(u, UpSubunit)
    u.id2idx2value[int64(3)][int64(0)] = float64(2.0)
    u.scale_up()
    assert numpy.isnan(u.id2idx2value[int64(3)][int64(0)])
    assert numpy.isnan(u.name2idx2value["land_lahn_kalk"][int64(0)])


@pytest.mark.parametrize(
    "task_subunit",
    [
        (UpSubunit, constants.UP_A, TransSubunit),
        (UpSubunit, constants.UP_G, TransSubunit),
        (UpSubunit, constants.UP_H, TransSubunit),
        (UpSubunit, numpy.max, TransSubunit),
    ],
    indirect=True,
)
def test_raster_subunit_default_upscaler_missing_value(
    task_subunit: managing.RasterSubunitTask,
) -> None:
    o = task_subunit.regionaliser.output
    u = task_subunit.upscaler
    e = task_subunit.regionaliser.group.element_raster.values
    s = task_subunit.regionaliser.group.subunit_raster.values
    o[u.mask * (e == 3) * (s == 0)] = numpy.nan, 2.0
    assert isinstance(u, UpSubunit)
    assert len(u.id2idx2value) == 5
    assert len(u.id2idx2value[int64(2)]) == 4
    assert len(u.id2idx2value[int64(3)]) == 7
    u.id2idx2value[int64(3)][int64(0)] = float64(2.0)
    u.scale_up()
    assert isinstance(u, UpSubunit)
    assert numpy.isnan(u.id2idx2value[int64(3)][int64(0)])
    assert numpy.isnan(u.name2idx2value["land_lahn_kalk"][int64(0)])
