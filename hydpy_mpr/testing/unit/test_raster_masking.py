# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import managing
from hydpy_mpr.source import transforming
from hydpy_mpr.source import upscaling

UpSubunit = upscaling.RasterSubunitDefaultUpscaler
TransSubunit = transforming.RasterSubunitIdentityTransformer


@pytest.mark.parametrize(
    "task_subunit", [(UpSubunit, constants.UP_A, TransSubunit)], indirect=True
)
def test_raster_masking(task_subunit: managing.RasterSubunitTask) -> None:
    mask = task_subunit.upscaler.mask
    equation = task_subunit.equation
    element = equation.group.element_raster
    subunit = equation.group.subunit_raster
    clay = equation.data_clay  # type: ignore[attr-defined]
    density = equation.data_density  # type: ignore[attr-defined]
    assert not numpy.any(numpy.isnan(clay.values[mask]))
    assert not numpy.any(numpy.isnan(density.values[mask]))
    assert not numpy.any(element.values[mask] == -9999)
    assert not numpy.any(subunit.values[mask] == -9999)
    assert numpy.array_equal(
        mask, element.mask * subunit.mask * clay.mask * density.mask
    )
