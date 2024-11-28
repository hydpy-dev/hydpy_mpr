from __future__ import annotations
import abc
import dataclasses

from hydpy_mpr.source import equations
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class RasterPreprocessor(equations.RasterEquation, abc.ABC):

    @override
    def activate(self, *, raster_groups: reading.RasterGroups) -> None:
        super().activate(raster_groups=raster_groups)
        self.preprocess_data()
        self.group.data_rasters[self.name] = reading.RasterFloat(values=self.output)

    @abc.abstractmethod
    def preprocess_data(self) -> None:
        pass
