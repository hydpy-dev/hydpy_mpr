import hydpy_mpr as mpr
import numpy


class RasterMean(mpr.RasterUpscaler):

    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.task.equation.output
        id_raster = self.task.equation.group.id_raster.values
        for id_ in id2value:
            id2value[id_] = numpy.nanmean(output[numpy.where(id_ == id_raster)])
