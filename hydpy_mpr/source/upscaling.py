from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import managing
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass
class RasterUpscaler(abc.ABC):

    mpr: managing.MPR = dataclasses.field(init=False)
    task: managing.RasterTask[Any] = dataclasses.field(init=False)

    def activate(self, mpr: managing.MPR, /, *, task: managing.RasterTask[Any]) -> None:
        self.mpr = mpr
        self.task = task

    @abc.abstractmethod
    def scale_up(self) -> None:
        pass


@dataclasses.dataclass
class RasterElementUpscaler(RasterUpscaler, abc.ABC):

    id2value: dict[int64, float64] = dataclasses.field(init=False)

    @override
    def activate(self, mpr: managing.MPR, /, *, task: managing.RasterTask[Any]) -> None:
        super().activate(mpr, task=task)
        self.id2value = {
            id_: float64(numpy.nan) for id_ in self.task.equation.group.id2element
        }

    @property
    def name2value(self) -> dict[str, float64]:
        id2element = self.task.equation.group.id2element
        return {id2element[id_]: value for id_, value in self.id2value.items()}


@dataclasses.dataclass
class RasterSubunitUpscaler(RasterUpscaler, abc.ABC):

    id2idx2value: dict[int64, dict[int64, float]] = dataclasses.field(init=False)

    @override
    def activate(self, mpr: managing.MPR, /, *, task: managing.RasterTask[Any]) -> None:
        super().activate(mpr, task=task)
        element_raster = self.task.equation.group.element_raster.values
        id2idx2value = {}
        for id_ in self.task.equation.group.id2element:
            idx2value = {}
            idxs = numpy.unique(element_raster[numpy.where(element_raster == id_)])
            for idx in sorted(idxs):
                idx2value[idx] = numpy.nan
            id2idx2value[id_] = idx2value
        self.id2idx2value = id2idx2value
