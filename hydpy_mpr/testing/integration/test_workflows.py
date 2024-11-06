# pylint: disable=missing-docstring, unused-argument

from __future__ import annotations
from dataclasses import dataclass, field

from hydpy import HydPy, nse, pub
from hydpy.models.hland.hland_control import FC
from numpy import float64, nanmean, where
from pytest import approx, mark

from hydpy_mpr import (
    Calibrator,
    Coefficient,
    Config,
    RasterEquation,
    RasterFloat,
    RasterTask,
    RasterTransformer,
    RasterUpscaler,
    TP,
)
from hydpy_mpr.source.reading import read_rastergroups


@mark.integration_test
def test_raster_workflow(fixture_project: None) -> None:

    @dataclass
    class RasterEquationFC(RasterEquation):

        file_sand: str
        file_clay: str

        data_sand: RasterFloat = field(init=False)
        data_clay: RasterFloat = field(init=False)

        coef_const: Coefficient
        coef_factor_sand: Coefficient
        coef_factor_clay: Coefficient

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
        coef_const=Coefficient(name="const", default=200.0),
        coef_factor_sand=Coefficient(name="factor_sand", default=0.0),
        coef_factor_clay=Coefficient(name="factor_clay", default=0.0),
    )

    raster_groups = read_rastergroups("HydPy-H-Lahn/mpr_data")
    fc.extract_rasters(raster_groups=raster_groups)

    fc.coef_factor_sand.value = -100.0
    fc.coef_factor_clay.value = 300.0

    fc.apply_coefficients()
    fc.apply_mask()

    class RasterMean(RasterUpscaler):
        def scale_up(self) -> None:
            id2value = self.id2value
            output = self.equation.output
            id_raster = self.equation.group.id_raster
            for id_ in id2value:
                id2value[id_] = nanmean(output[where(id_ == id_raster.values)])

    fc_upscaler = RasterMean(fc)
    fc_upscaler.scale_up()

    class RasterIdentityTransformer(RasterTransformer[TP]):

        def modify_parameter(self, parameter: TP, value: float64) -> None:
            parameter(value)

    transformer = RasterIdentityTransformer(hland_96=FC)

    hp = HydPy("HydPy-H-Lahn")
    pub.timegrids = "1996-01-01", "1997-01-01", "1d"
    hp.prepare_everything()

    transformer.activate(selection=pub.selections.complete, upscaler=fc_upscaler)
    transformer.modify_parameters()


    class MyCalibrator(Calibrator):

        def calculate_likelihood(self) -> float:
            return sum(nse(node=node) for node in self.hp.nodes) / 4.0

    calib = MyCalibrator()

    config = Config(
        calibrator=calib,
        tasks=[
            RasterTask(equation=fc, upscaler=fc_upscaler, transformers=[transformer])
        ]
    )

    calib.activate(hp=hp, config=config)

    likelihood, values = calib.run(maxeval=100)
    assert likelihood == approx(0.82529)
    assert values == approx([-1882.091759, 972.689725, -259.809734])
    fc_values = hp.elements["land_dill_assl"].model.parameters.control.fc.values
    assert min(fc_values) == max(fc_values) == approx(278.732232)
