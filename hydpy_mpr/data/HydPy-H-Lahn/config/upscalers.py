import hydpy_mpr as mpr
import numpy


class RasterMean(mpr.RasterUpscaler):

    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.equation.output
        id_raster = self.equation.group.id_raster
        for id_ in id2value:
            id2value[id_] = numpy.nanmean(output[numpy.where(id_ == id_raster)])