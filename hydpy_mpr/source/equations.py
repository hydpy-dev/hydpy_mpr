from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import reading
from hydpy_mpr.source import utilities
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class RasterEquation(abc.ABC):

    dir_group: utilities.NewTypeDataclassDescriptor[str, NameRasterGroup] = (
        utilities.NewTypeDataclassDescriptor()
    )
    name: NameRaster = dataclasses.field(default=NameRaster(""))
    group: reading.RasterGroup = dataclasses.field(init=False)
    mask: MatrixBool = dataclasses.field(init=False)
    output: MatrixFloat = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        if not self.name:
            self.name = NameRaster(type(self).__qualname__.lower())

    def activate(self, *, raster_groups: reading.RasterGroups) -> None:
        group = raster_groups[self.dir_group]
        self.group = group
        self.mask = numpy.full(self.shape, True, dtype=bool)
        for fieldname, filename in self.fieldname2rasterame.items():
            rastername = f"data_{fieldname.removeprefix('file_')}"
            raster = group.data_rasters[filename]  # ToDo: error message
            setattr(self, rastername, raster)  # ToDo: check type?
            self.mask *= raster.mask
        self.output = numpy.full(self.shape, numpy.nan)

    @property
    def shape(self) -> tuple[int, int]:
        shape = self.group.shape
        assert isinstance(shape, tuple)
        assert len(shape) == 2
        return shape

    @property
    def fieldname2rasterame(self) -> dict[str, NameRaster]:
        return {
            field.name: NameRaster(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if (field.name).startswith("file_")
        }

    @property
    def inputs(self) -> Mapping[str, reading.RasterFloat]:
        return {
            name: value
            for field in dataclasses.fields(self)
            if ((name := field.name) != "output")
            and isinstance(value := getattr(self, name), reading.RasterFloat)
        }

    def apply_mask(self) -> None:
        self.output[~self.mask] = numpy.nan
