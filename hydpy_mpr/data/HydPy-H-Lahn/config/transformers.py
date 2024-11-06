import hydpy_mpr as mpr
import numpy


class RasterIdentityTransformer(mpr.RasterTransformer[mpr.TP]):

    def modify_parameter(self, parameter: mpr.TP, value: numpy.float64) -> None:
        parameter(value)
