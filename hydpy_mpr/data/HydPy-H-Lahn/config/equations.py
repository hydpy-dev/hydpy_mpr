import dataclasses
import hydpy_mpr


@dataclasses.dataclass
class FC(hydpy_mpr.RasterEquation):
    file_sand: str
    file_clay: str

    data_sand: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    data_clay: hydpy_mpr.RasterFloat = dataclasses.field(init=False)

    coef_const: hydpy_mpr.Coefficient
    coef_factor_sand: hydpy_mpr.Coefficient
    coef_factor_clay: hydpy_mpr.Coefficient

    def apply_coefficients(self) -> None:
        self.output[:] = (
            self.coef_const.value
            + self.coef_factor_sand.value * self.data_sand.values / 100.0
            + self.coef_factor_clay.value * self.data_clay.values / 100.0
        )
