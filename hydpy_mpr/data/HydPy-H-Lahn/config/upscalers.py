from hydpy_mpr import RasterUpscaler
from numpy import nanmean, where


class RasterMean(RasterUpscaler):

    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.equation.output
        id_raster = self.equation.group.id_raster
        for id_ in id2value:
            id2value[id_] = nanmean(output[where(id_ == id_raster)])