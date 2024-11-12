import dataclasses
import hydpy_mpr


@dataclasses.dataclass
class FC(hydpy_mpr.RasterEquation):
    file_clay: str
    file_density: str

    data_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    data_density: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_const: hydpy_mpr.Coefficient
    coef_factor_clay: hydpy_mpr.Coefficient
    coef_factor_density: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = 15.0 * (
            self.coef_const.value
            + self.coef_factor_clay.value * self.data_clay.values
            + self.coef_factor_density.value * self.data_density.values
        )
