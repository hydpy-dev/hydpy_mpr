import abc
import dataclasses

import numpy

import hydpy_mpr


@dataclasses.dataclass(kw_only=True)
class FC(hydpy_mpr.RasterRegionaliser, abc.ABC):

    file_clay: str
    file_density: str

    data_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    data_density: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_const: hydpy_mpr.Coefficient
    coef_factor_clay: hydpy_mpr.Coefficient
    coef_factor_density: hydpy_mpr.Coefficient


@dataclasses.dataclass(kw_only=True)
class FC2m(FC):

    def apply_coefficients(self) -> None:
        self.output[:] = 20.0 * (
            self.coef_const.value
            + self.coef_factor_clay.value * self.data_clay.values
            + self.coef_factor_density.value * self.data_density.values
        )


@dataclasses.dataclass(kw_only=True)
class FCFlex(FC):

    file_depth: str

    data_depth: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    def apply_coefficients(self) -> None:
        self.output[:] = (
            10.0
            * self.data_depth.values
            * (
                self.coef_const.value
                + self.coef_factor_clay.value * self.data_clay.values
                + self.coef_factor_density.value * self.data_density.values
            )
        )


@dataclasses.dataclass(kw_only=True)
class Beta(hydpy_mpr.RasterRegionaliser):

    file_density: str

    data_density: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_factor_density: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = self.coef_factor_density.value * self.data_density.values


@dataclasses.dataclass(kw_only=True)
class Ks(hydpy_mpr.RasterRegionaliser):

    file_sand: str
    file_clay: str

    data_sand: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    data_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_factor: hydpy_mpr.Coefficient
    coef_factor_sand: hydpy_mpr.Coefficient
    coef_factor_clay: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = self.coef_factor * numpy.exp(
            self.coef_factor_sand.value * self.data_sand.values
            - self.coef_factor_clay.value * self.data_clay.values
        )


@dataclasses.dataclass(kw_only=True)
class PercMax(hydpy_mpr.RasterRegionaliser):

    file_ks: str

    data_ks: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_factor: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = self.coef_factor.value * (1.0 + self.data_ks.values)
