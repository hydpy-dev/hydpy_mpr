# pylint: disable=missing-docstring, unused-argument

from __future__ import annotations
import dataclasses
import os

import hydpy
from hydpy import pub
from hydpy.models.hland import hland_control
import pytest

import hydpy_mpr
from hydpy_mpr.source.typing_ import *


@pytest.mark.integration_test
def test_raster_workflow(arrange_project: None) -> None:

    @dataclasses.dataclass
    class RasterEquationFC(hydpy_mpr.RasterEquation):

        file_clay: str
        file_density: str

        data_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
        data_density: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

        coef_const: hydpy_mpr.Coefficient
        coef_factor_clay: hydpy_mpr.Coefficient
        coef_factor_density: hydpy_mpr.Coefficient

        @override
        def apply_coefficients(self) -> None:
            self.output[:] = 20.0 * (
                self.coef_const.value
                + self.coef_factor_clay.value * self.data_clay.values
                + self.coef_factor_density.value * self.data_density.values
            )

    fc = RasterEquationFC(
        dir_group="raster_15km",
        file_clay="clay_mean_0_200_res15km_pct",
        file_density="bdod_mean_0_200_res15km_gcm3",
        coef_const=hydpy_mpr.Coefficient(
            name="const", default=20.0, lower=5.0, upper=50.0
        ),
        coef_factor_clay=hydpy_mpr.Coefficient(
            name="factor_clay", default=0.5, lower=0.0, upper=1.0
        ),
        coef_factor_density=hydpy_mpr.Coefficient(
            name="factor_density", default=-1.0, lower=-5.0, upper=0.0
        ),
    )

    class MyCalibrator(hydpy_mpr.NLOptCalibrator):

        @override
        def calculate_likelihood(self) -> float:
            return sum(hydpy.nse(node=node) for node in self.hp.nodes) / 4.0

    hp = hydpy.HydPy("HydPy-H-Lahn")
    pub.timegrids = "1996-01-01", "1997-01-01", "1d"
    hp.prepare_everything()

    mpr = hydpy_mpr.MPR(
        mprpath=os.path.join("HydPy-H-Lahn", "mpr_data"),
        hp=hp,
        tasks=[
            hydpy_mpr.RasterSubunitTask(
                equation=fc,
                upscaler=hydpy_mpr.RasterSubunitDefaultUpscaler(),
                transformers=[
                    hydpy_mpr.RasterSubunitIdentityTransformer(
                        parameter=hland_control.FC, model="hland_96"
                    )
                ],
            )
        ],
        calibrator=MyCalibrator(maxeval=100),
        writers=[hydpy_mpr.ControlWriter(controldir="experiment_1")],
    )

    mpr.run()
    assert mpr.calibrator.likelihood == pytest.approx(0.818256247212652)
    assert mpr.calibrator.values == pytest.approx(
        [5.0, 0.5267278445642123, -4.9999999999925]
    )
    fc_values = hp.elements["land_dill_assl"].model.parameters.control.fc.values
    assert fc_values == pytest.approx(
        [
            278.0,
            278.0,
            278.0,
            278.0,
            280.47638276,
            264.40416301,
            278.0,
            278.0,
            278.0,
            278.0,
            278.0,
            278.0,
        ]
    )
