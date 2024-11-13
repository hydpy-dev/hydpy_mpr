# pylint: disable=missing-docstring, unused-argument

from hydpy.models.hland import hland_control
import numpy

from hydpy_mpr.source import managing


def test_raster_masking(task_15km: managing.RasterTask[hland_control.FC]) -> None:
    mask = task_15km.mask
    equation = task_15km.equation
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
