# pylint: disable=missing-docstring, unused-argument

import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source.typing_ import *


def test_grid_calibrator_nmb_nodes_1_okay(
    gridcalibrator_with_dummy_coefficients: type[hydpy_mpr.GridCalibrator],
) -> None:
    c = gridcalibrator_with_dummy_coefficients(nmb_nodes=1)
    values = tuple(c.gridpoints)
    assert len(values) == 1
    assert values[0] == (0.0, 4.0)


def test_grid_calibrator_nmb_nodes_3_okay(
    gridcalibrator_with_dummy_coefficients: type[hydpy_mpr.GridCalibrator],
) -> None:
    c = gridcalibrator_with_dummy_coefficients(nmb_nodes=3)
    values = tuple(c.gridpoints)
    assert len(values) == 9
    assert values == (
        (-1.0, 2.0),
        (-1.0, 4.0),
        (-1.0, 6.0),
        (0.0, 2.0),
        (0.0, 4.0),
        (0.0, 6.0),
        (1.0, 2.0),
        (1.0, 4.0),
        (1.0, 6.0),
    )


def test_grid_calibrator_missing_bounds(
    gridcalibrator_with_dummy_coefficients: type[hydpy_mpr.GridCalibrator],
) -> None:
    c = gridcalibrator_with_dummy_coefficients(nmb_nodes=1)
    c.coefficients[1].upper = numpy.inf
    with pytest.raises(ValueError) as info:
        tuple(c.gridpoints)
    assert str(info.value) == (
        "Class `TestGridCalibrator` requires lower and upper bounds for all "
        "coefficients, but coefficient `c2` defines no upper bound."
    )
    c.coefficients[0].lower = -numpy.inf
    with pytest.raises(ValueError) as info:
        tuple(c.gridpoints)
    assert str(info.value) == (
        "Class `TestGridCalibrator` requires lower and upper bounds for all "
        "coefficients, but coefficient `c1` defines no lower bound."
    )


def test_grid_calibrator_calibrate(
    monkeypatch: pytest.MonkeyPatch,
    gridcalibrator_with_dummy_coefficients: type[hydpy_mpr.GridCalibrator],
) -> None:

    last_values: Sequence[float] = (9.0, 9.0)
    times_called = 0

    def perform_calibrationstep(
        self: hydpy_mpr.GridCalibrator, values: Sequence[float]
    ) -> float:
        nonlocal times_called, last_values
        times_called += 1
        last_values = values
        return 1.0 if values == (0.0, 4.0) else 0.0

    c = gridcalibrator_with_dummy_coefficients(nmb_nodes=3)
    monkeypatch.setattr(
        hydpy_mpr.GridCalibrator, "perform_calibrationstep", perform_calibrationstep
    )
    c.calibrate()
    assert times_called == 9 + 1
    assert last_values == (0.0, 4.0)
    assert c.likelihood == 1.0
