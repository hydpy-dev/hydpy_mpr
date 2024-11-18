# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

from hydpy_mpr.source import regionalising


def test_raster_regionaliser_fc(
    dirpath_mpr_data: str, regionaliser_fc: regionalising.RasterRegionaliser
) -> None:
    r = regionaliser_fc
    r.apply_coefficients()
    assert numpy.nanmin(r.output) == pytest.approx(256.26911878585815)
    assert numpy.nanmean(r.output) == pytest.approx(291.50745650132495)
    assert numpy.nanmax(r.output) == pytest.approx(324.20000076293945)
    const, factor_clay, factor_density = r.coefficients
    data_clay, data_density = r.inputs.values()
    i_max = numpy.nanargmax(r.output.flatten())
    fc_max = 20.0 * (
        const.value
        + factor_clay.value * data_clay.values.flatten()[i_max]
        + factor_density.value * data_density.values.flatten()[i_max]
    )
    assert fc_max == pytest.approx(324.20000076293945)
