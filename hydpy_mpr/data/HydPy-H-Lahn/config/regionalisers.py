import abc
import dataclasses

import numpy

import hydpy_mpr


@dataclasses.dataclass(kw_only=True)
class FC(hydpy_mpr.RasterRegionaliser, abc.ABC):

    source_clay: str
    source_density: str

    dataset_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    dataset_density: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_const: hydpy_mpr.Coefficient
    coef_factor_clay: hydpy_mpr.Coefficient
    coef_factor_density: hydpy_mpr.Coefficient


@dataclasses.dataclass(kw_only=True)
class FC2m(FC):

    def apply_coefficients(self) -> None:
        self.output[:] = 20.0 * (
            self.coef_const.value
            + self.coef_factor_clay.value * self.dataset_clay.values
            + self.coef_factor_density.value * self.dataset_density.values
        )


@dataclasses.dataclass(kw_only=True)
class FCFlex(FC):

    source_depth: str

    dataset_depth: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    def apply_coefficients(self) -> None:
        self.output[:] = (
            10.0
            * self.dataset_depth.values
            * (
                self.coef_const.value
                + self.coef_factor_clay.value * self.dataset_clay.values
                + self.coef_factor_density.value * self.dataset_density.values
            )
        )


@dataclasses.dataclass(kw_only=True)
class Beta(hydpy_mpr.RasterRegionaliser):

    source_density: str

    dataset_density: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_factor_density: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = self.coef_factor_density.value * self.dataset_density.values


@dataclasses.dataclass(kw_only=True)
class KS(hydpy_mpr.RasterSubregionaliser):

    source_sand: str
    source_clay: str

    dataset_sand: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    dataset_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_factor: hydpy_mpr.Coefficient
    coef_factor_sand: hydpy_mpr.Coefficient
    coef_factor_clay: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = self.coef_factor.value * numpy.exp(
            self.coef_factor_sand.value * self.dataset_sand.values
            - self.coef_factor_clay.value * self.dataset_clay.values
        )


@dataclasses.dataclass(kw_only=True)
class PercMax(hydpy_mpr.RasterRegionaliser):

    source_ks: str

    dataset_ks: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_factor: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = self.coef_factor.value * (1.0 + self.dataset_ks.values)


@dataclasses.dataclass(kw_only=True)
class K(hydpy_mpr.RasterRegionaliser):

    source_ks: str
    source_dh: str

    dataset_ks: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    dataset_dh: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_const: hydpy_mpr.Coefficient
    coef_factor_ks: hydpy_mpr.Coefficient
    coef_factor_dh: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = (
            self.coef_const.value
            + self.coef_factor_ks.value * (1.0 + self.dataset_ks.values)
            + self.coef_factor_dh.value * (1.0 + self.dataset_dh.values)
        )
