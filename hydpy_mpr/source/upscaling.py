from __future__ import annotations
import abc
import dataclasses

import numpy
from scipy import stats

from hydpy_mpr.source import constants
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


@dataclasses.dataclass
class RasterElementDefaultUpscaler(RasterElementUpscaler):

    function: UpscalingOption = constants.UP_A
    _function: UpscalingFunction = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._function = _query_function(self.function)

    @override
    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.task.equation.output[self.task.mask]
        group = self.task.equation.group
        id_raster = group.element_raster.values[self.task.mask]
        function = self._function
        for id_ in id2value:
            idxs = id_ == id_raster
            if numpy.any(idxs):
                id2value[id_] = function(output[idxs])
            else:
                id2value[id_] = float64(numpy.nan)


def _query_function(function: UpscalingOption) -> UpscalingFunction:
    match function:
        case constants.UP_A:
            return numpy.mean
        case constants.UP_H:
            return stats.hmean  # type: ignore[no-any-return]
        case constants.UP_G:
            return stats.gmean  # type: ignore[no-any-return]
        case _:
            return function
