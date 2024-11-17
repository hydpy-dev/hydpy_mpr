# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

from hydpy_mpr.source import regionalising


def test_raster_equation_fc(
    dirpath_mpr_data: str, equation_fc: regionalising.RasterEquation
) -> None:
    equation_fc.apply_coefficients()
    assert numpy.nanmin(equation_fc.output) == pytest.approx(256.26911878585815)
    assert numpy.nanmean(equation_fc.output) == pytest.approx(291.50745650132495)
    assert numpy.nanmax(equation_fc.output) == pytest.approx(324.20000076293945)
    e = equation_fc
    const, factor_clay, factor_density = e.coefficients
    data_clay, data_density = e.inputs.values()
    i_max = numpy.nanargmax(e.output.flatten())
    fc_max = 20.0 * (
        const.value
        + factor_clay.value * data_clay.values.flatten()[i_max]
        + factor_density.value * data_density.values.flatten()[i_max]
    )
    assert fc_max == pytest.approx(324.20000076293945)
