import dataclasses
import hydpy_mpr as mpr


@dataclasses.dataclass
class FC(mpr.RasterEquation):
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
                + self.coef_factor_sand.value * self.data_sand.values
                + self.coef_factor_clay.value * self.data_clay.values
        )


