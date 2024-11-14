# pylint: disable=missing-docstring, unused-argument

from __future__ import annotations
import dataclasses
import os

import hydpy
from hydpy import pub
from hydpy.models.hland import hland_control
import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source.typing_ import *


@pytest.mark.integration_test
def test_raster_workflow(arrange_project: None) -> None:

    @dataclasses.dataclass
    class RasterEquationFC(hydpy_mpr.RasterEquation):

        file_sand: str
        file_clay: str

        data_sand: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
        data_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

        coef_const: hydpy_mpr.Coefficient
        coef_factor_sand: hydpy_mpr.Coefficient
        coef_factor_clay: hydpy_mpr.Coefficient

        @override
        def apply_coefficients(self) -> None:
            self.output[:] = (
                self.coef_const.value
                + self.coef_factor_sand.value * self.data_sand.values / 100.0
                + self.coef_factor_clay.value * self.data_clay.values / 100.0
            )

    fc = RasterEquationFC(
        dir_group="raster_5km",
        file_sand="sand_mean_0_200_res5km",
        file_clay="clay_mean_0_200_res5km",
        coef_const=hydpy_mpr.Coefficient(name="const", default=200.0),
        coef_factor_sand=hydpy_mpr.Coefficient(name="factor_sand", default=-100.0),
        coef_factor_clay=hydpy_mpr.Coefficient(name="factor_clay", default=300.0),
    )

    class RasterMean(hydpy_mpr.RasterElementUpscaler):
        @override
        def scale_up(self) -> None:
            id2value = self.id2value
            output = self.equation.output
            id_raster = self.equation.group.element_raster
            for id_ in id2value:
                id2value[id_] = numpy.nanmean(
                    output[numpy.where(id_ == id_raster.values)]
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
            hydpy_mpr.RasterElementTask(
                equation=fc,
                upscaler=RasterMean(),
                transformers=[
                    hydpy_mpr.RasterElementIdentityTransformer(
                        parameter=hland_control.FC, model="hland_96"
                    )
                ],
            )
        ],
        calibrator=MyCalibrator(maxeval=100),
        writers=[hydpy_mpr.ControlWriter(controldir="experiment_1")],
    )

    mpr.run()
    assert mpr.calibrator.likelihood == pytest.approx(0.8252895637383195)
    assert mpr.calibrator.values == pytest.approx(
        [-1882.09175855596, 972.6897246013439, -259.8097340328786]
    )
    fc_values = hp.elements["land_dill_assl"].model.parameters.control.fc.values
    assert min(fc_values) == max(fc_values) == pytest.approx(278.73223239535025)
