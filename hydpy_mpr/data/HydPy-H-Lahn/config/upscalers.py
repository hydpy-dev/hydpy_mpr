import hydpy_mpr
import numpy


class RasterElementMean(hydpy_mpr.RasterElementUpscaler):

    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.task.equation.output
        id_raster = self.task.equation.group.element_raster.values
        for id_ in id2value:
            id2value[id_] = numpy.nanmean(output[numpy.where(id_ == id_raster)])


class RasterSubunitMean(hydpy_mpr.RasterSubunitUpscaler):

    def scale_up(self) -> None:
        output = self.task.equation.output
        element_raster = self.task.equation.group.element_raster.values
        subunit_raster = self.task.equation.group.subunit_raster.values
        for id_, idx2value in self.id2idx2value.items():
            idx_raster_element = element_raster == id_
            for idx in idx2value:
                idx_raster_subunit = idx_raster_element * (subunit_raster == idx)
                idx2value[idx] = numpy.nanmean(output[idx_raster_subunit])
