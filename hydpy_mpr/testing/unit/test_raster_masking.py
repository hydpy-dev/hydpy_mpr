# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source import constants

UpSubunit = hydpy_mpr.RasterSubunitDefaultUpscaler
TransSubunit = hydpy_mpr.SubunitIdentityTransformer


@pytest.mark.parametrize(
    "task_raster_subunit", [(UpSubunit, constants.UP_A, TransSubunit)], indirect=True
)
def test_raster_masking(task_raster_subunit: hydpy_mpr.RasterSubunitTask) -> None:
    mask = task_raster_subunit.upscaler.mask
    regionaliser = task_raster_subunit.regionaliser
    element = regionaliser.provider_.element_id
    subunit = regionaliser.provider_.subunit_id
    clay = regionaliser.dataset_clay  # type: ignore[attr-defined]
    density = regionaliser.dataset_density  # type: ignore[attr-defined]
    assert not numpy.any(numpy.isnan(clay.values[mask]))
    assert not numpy.any(numpy.isnan(density.values[mask]))
    assert not numpy.any(element.values[mask] == -9999)
    assert not numpy.any(subunit.values[mask] == -9999)
    assert numpy.array_equal(
        mask, element.mask * subunit.mask * clay.mask * density.mask
    )
