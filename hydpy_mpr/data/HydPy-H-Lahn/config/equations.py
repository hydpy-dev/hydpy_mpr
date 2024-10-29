
from dataclasses import dataclass, field

from hydpy_mpr import Coefficient, RasterEquation, RasterFloat


@dataclass
class FC(RasterEquation):
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
                + self.coef_factor_sand.value * self.data_sand.values
                + self.coef_factor_clay.value * self.data_clay.values
        )


