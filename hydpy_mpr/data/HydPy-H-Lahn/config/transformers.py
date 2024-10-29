
from hydpy_mpr import RasterTransformer, TP
from numpy import float64


class RasterIdentityTransformer(RasterTransformer[TP]):

    def modify_parameter(self, parameter: TP, value: float64) -> None:
        parameter(value)
