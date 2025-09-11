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
    "task_raster_element",
    [(UpElement, constants.UP_A, TransElement, "mainmodel")],
    indirect=True,
)
def test_element_identity_transformer_for_mainmodel(
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
    "task_raster_element",
    [(UpElement, constants.UP_A, TransElement, "submodel")],
    indirect=True,
)
def test_element_identity_transformer_for_submodel(
    task_raster_element: hydpy_mpr.RasterElementTask,
) -> None:
    u = task_raster_element.upscaler
    assert isinstance(u, UpElement)
    u.id2value[int64(3)] = float64(0.5)
    t = task_raster_element.transformers[0]
    t.modify_parameters()
    sml = (
        t.hp.elements["land_lahn_kalk"]
        .model.aetmodel.parameters.control["soilmoisturelimit"]
        .values
    )
    assert numpy.min(sml) == numpy.max(sml) == 0.5
    u.id2value[int64(3)] = float64(numpy.nan)
    t.modify_parameters()
    assert numpy.min(sml) == numpy.max(sml) == 0.5


@pytest.mark.parametrize(
    "task_raster_element",
    [(UpElement, constants.UP_A, TransElement, "subsubmodel")],
    indirect=True,
)
def test_element_identity_transformer_for_subsubmodel(
    task_raster_element: hydpy_mpr.RasterElementTask,
) -> None:
    u = task_raster_element.upscaler
    assert isinstance(u, UpElement)
    u.id2value[int64(3)] = float64(0.5)
    t = task_raster_element.transformers[0]
    t.modify_parameters()
    etf = (
        t.hp.elements["land_lahn_kalk"]
        .model.aetmodel.petmodel.parameters.control["evapotranspirationfactor"]
        .values
    )
    assert numpy.min(etf) == numpy.max(etf) == 0.5
    u.id2value[int64(3)] = float64(numpy.nan)
    t.modify_parameters()
    assert numpy.min(etf) == numpy.max(etf) == 0.5


@pytest.mark.parametrize(
    "task_raster_subunit",
    [(UpSubunit, constants.UP_A, TransSubunit, "mainmodel")],
    indirect=True,
)
def test_subunit_identity_transformer_for_mainmodel(
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


@pytest.mark.parametrize(
    "task_raster_subunit",
    [(UpSubunit, constants.UP_A, TransSubunit, "submodel")],
    indirect=True,
)
def test_subunit_identity_transformer_for_submodel(
    task_raster_subunit: hydpy_mpr.RasterElementTask,
) -> None:
    u = task_raster_subunit.upscaler
    assert isinstance(u, UpSubunit)
    u.id2idx2value[int64(3)][int64(1)] = float64(0.5)
    u.id2idx2value[int64(3)][int64(3)] = float64(0.7)
    t = task_raster_subunit.transformers[0]
    t.modify_parameters()
    sml = (
        t.hp.elements["land_lahn_kalk"]
        .model.aetmodel.parameters.control["soilmoisturelimit"]
        .values
    )
    assert sml[1] == 0.5
    assert sml[2] == 0.9
    assert sml[3] == 0.7


@pytest.mark.parametrize(
    "task_raster_subunit",
    [(UpSubunit, constants.UP_A, TransSubunit, "subsubmodel")],
    indirect=True,
)
def test_subunit_identity_transformer_for_subsubmodel(
    task_raster_subunit: hydpy_mpr.RasterElementTask,
) -> None:
    u = task_raster_subunit.upscaler
    assert isinstance(u, UpSubunit)
    u.id2idx2value[int64(3)][int64(1)] = float64(0.5)
    u.id2idx2value[int64(3)][int64(3)] = float64(0.7)
    t = task_raster_subunit.transformers[0]
    t.modify_parameters()
    etf = (
        t.hp.elements["land_lahn_kalk"]
        .model.aetmodel.petmodel.parameters.control["evapotranspirationfactor"]
        .values
    )
    assert etf[1] == 0.5
    assert etf[2] == 1.0
    assert etf[3] == 0.7
