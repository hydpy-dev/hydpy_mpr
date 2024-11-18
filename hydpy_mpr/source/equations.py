from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class RasterEquation(abc.ABC):

    dir_group: str
    group: reading.RasterGroup = dataclasses.field(init=False)
    mask: MatrixFloat = dataclasses.field(init=False)
    output: MatrixFloat = dataclasses.field(init=False)

    def activate(self, *, raster_groups: reading.RasterGroups) -> None:
        group = raster_groups[self.dir_group]
        self.group = group
        self.mask = numpy.full(self.shape, True, dtype=bool)
        for fieldname, filename in self.fieldname2filename.items():
            rastername = f"data_{fieldname.removeprefix('file_')}"
            raster = group.data_rasters[filename]
            setattr(self, rastername, raster)
            self.mask *= raster.mask
        self.output = numpy.full(self.shape, numpy.nan)

    @property
    def shape(self) -> tuple[int, int]:
        shape = self.group.shape
        assert isinstance(shape, tuple)
        assert len(shape) == 2
        return shape

    @property
    def fieldname2filename(self) -> dict[str, str]:
        return {
            field.name: getattr(self, field.name)
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
