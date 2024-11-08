import hydpy_mpr
import numpy


class RasterIdentityTransformer(hydpy_mpr.RasterTransformer[hydpy_mpr.TP]):

    def modify_parameter(self, parameter: hydpy_mpr.TP, value: numpy.float64) -> None:
        parameter(value)
