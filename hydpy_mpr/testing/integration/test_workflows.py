# pylint: disable=missing-docstring, unused-argument

from __future__ import annotations
import dataclasses

import hydpy
from hydpy import pub
from hydpy.models.hland import hland_control
import numpy
import pytest

import hydpy_mpr as mpr
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


@pytest.mark.integration_test
def test_raster_workflow(fixture_project: None) -> None:

    @dataclasses.dataclass
    class RasterEquationFC(mpr.RasterEquation):

        file_sand: str
        file_clay: str

        data_sand: mpr.RasterFloat = dataclasses.field(init=False)
        data_clay: mpr.RasterFloat = dataclasses.field(init=False)

        coef_const: mpr.Coefficient
        coef_factor_sand: mpr.Coefficient
        coef_factor_clay: mpr.Coefficient

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
        coef_const=mpr.Coefficient(name="const", default=200.0),
        coef_factor_sand=mpr.Coefficient(name="factor_sand", default=0.0),
        coef_factor_clay=mpr.Coefficient(name="factor_clay", default=0.0),
    )

    raster_groups = reading.read_rastergroups("HydPy-H-Lahn/mpr_data")
    fc.extract_rasters(raster_groups=raster_groups)

    fc.coef_factor_sand.value = -100.0
    fc.coef_factor_clay.value = 300.0

    fc.apply_coefficients()
    fc.apply_mask()

    class RasterMean(mpr.RasterUpscaler):
        def scale_up(self) -> None:
            id2value = self.id2value
            output = self.equation.output
            id_raster = self.equation.group.id_raster
            for id_ in id2value:
                id2value[id_] = numpy.nanmean(
                    output[numpy.where(id_ == id_raster.values)]
                )

    fc_upscaler = RasterMean(fc)
    fc_upscaler.scale_up()

    class RasterIdentityTransformer(mpr.RasterTransformer[TP]):

        def modify_parameter(self, parameter: TP, value: float64) -> None:
            parameter(value)

    transformer = RasterIdentityTransformer(hland_96=hland_control.FC)

    hp = hydpy.HydPy("HydPy-H-Lahn")
    pub.timegrids = "1996-01-01", "1997-01-01", "1d"
    hp.prepare_everything()

    transformer.activate(selection=pub.selections.complete, upscaler=fc_upscaler)
    transformer.modify_parameters()

    class MyCalibrator(mpr.Calibrator):

        def calculate_likelihood(self) -> float:
            return sum(hydpy.nse(node=node) for node in self.hp.nodes) / 4.0

    calib = MyCalibrator()

    config = mpr.Config(
        hp=hp,
        tasks=[
            mpr.RasterTask(
                equation=fc, upscaler=fc_upscaler, transformers=[transformer]
            )
        ],
        calibrator=calib,
        runner=mpr.Runner(),
    )

    calib.activate(hp=hp, config=config)

    likelihood, values = calib.calibrate(maxeval=100)
    assert likelihood == pytest.approx(0.82529)
    assert values == pytest.approx([-1882.091759, 972.689725, -259.809734])
    fc_values = hp.elements["land_dill_assl"].model.parameters.control.fc.values
    assert min(fc_values) == max(fc_values) == pytest.approx(278.732232)
