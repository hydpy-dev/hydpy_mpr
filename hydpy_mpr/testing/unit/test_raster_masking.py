# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import managing
from hydpy_mpr.source import transforming
from hydpy_mpr.source import upscaling

UpElement = upscaling.RasterElementDefaultUpscaler
TransElement = transforming.RasterElementIdentityTransformer


@pytest.mark.parametrize(
    "task_element", [(UpElement, constants.UP_A, TransElement)], indirect=True
)
def test_raster_masking(task_element: managing.RasterElementTask) -> None:
    mask = task_element.upscaler.mask
    equation = task_element.equation
    element = equation.group.element_raster.values
    subunit = equation.group.subunit_raster.values
    clay = equation.data_clay.values  # type: ignore[attr-defined]
    density = equation.data_density.values  # type: ignore[attr-defined]
    product = element * subunit * clay * density
    assert numpy.array_equal(~numpy.isnan(product), mask)
    assert not numpy.any(numpy.isnan(clay[mask]))
    assert not numpy.any(numpy.isnan(density[mask]))
    assert not numpy.any(element[mask] == -9999)
    assert not numpy.any(subunit[mask] == -9999)
