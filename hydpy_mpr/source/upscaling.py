from __future__ import annotations
import abc
import dataclasses

import numpy
from scipy import stats

from hydpy_mpr.source import constants
from hydpy_mpr.source import regionalising
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class RasterUpscaler(abc.ABC):

    regionaliser: regionalising.RasterRegionaliser = dataclasses.field(init=False)
    mask: MatrixBool = dataclasses.field(init=False)

    def activate(self, *, regionaliser: regionalising.RasterRegionaliser) -> None:
        self.regionaliser = regionaliser
        self.mask = regionaliser.group.element_raster.mask.copy()
        for raster in regionaliser.inputs.values():
            self.mask *= raster.mask

    @abc.abstractmethod
    def scale_up(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class RasterElementUpscaler(RasterUpscaler, abc.ABC):

    id2value: dict[int64, float64] = dataclasses.field(init=False)

    @override
    def activate(self, *, regionaliser: regionalising.RasterRegionaliser) -> None:
        super().activate(regionaliser=regionaliser)
        self.id2value = {
            id_: float64(numpy.nan) for id_ in self.regionaliser.group.id2element
        }

    @property
    def name2value(self) -> dict[str, float64]:
        id2element = self.regionaliser.group.id2element
        return {id2element[id_]: value for id_, value in self.id2value.items()}


@dataclasses.dataclass(kw_only=True)
class RasterSubunitUpscaler(RasterUpscaler, abc.ABC):

    id2idx2value: dict[int64, dict[int64, float64]] = dataclasses.field(init=False)

    @override
    def activate(self, *, regionaliser: regionalising.RasterRegionaliser) -> None:
        super().activate(regionaliser=regionaliser)

        self.mask *= (
            regionaliser.group.subunit_raster.mask
        )  # ToDo: better error message

        element_raster = regionaliser.group.element_raster.values
        subunit_raster = regionaliser.group.subunit_raster.values
        id2idx2value = {}
        for id_ in regionaliser.group.id2element:
            idx2value = {}
            idxs = numpy.unique(subunit_raster[numpy.where(element_raster == id_)])
            for idx in sorted(idxs):
                idx2value[int64(idx)] = float64(numpy.nan)
            id2idx2value[id_] = idx2value
        self.id2idx2value = id2idx2value

    @property
    def name2idx2value(self) -> dict[str, dict[int64, float64]]:
        id2element = self.regionaliser.group.id2element
        return {id2element[id_]: value for id_, value in self.id2idx2value.items()}


@dataclasses.dataclass(kw_only=True)
class RasterElementDefaultUpscaler(RasterElementUpscaler):

    function: UpscalingOption = constants.UP_A
    _function: UpscalingFunction = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._function = _query_function(self.function)

    @override
    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.regionaliser.output[self.mask]
        group = self.regionaliser.group
        id_raster = group.element_raster.values[self.mask]
        function = self._function
        for id_ in id2value:
            idxs = id_ == id_raster
            if numpy.any(idxs):
                id2value[id_] = function(output[idxs])
            else:
                id2value[id_] = float64(numpy.nan)


@dataclasses.dataclass(kw_only=True)
class RasterSubunitDefaultUpscaler(RasterSubunitUpscaler):

    function: UpscalingOption = constants.UP_A
    _function: UpscalingFunction = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._function = _query_function(self.function)

    @override
    def scale_up(self) -> None:
        output = self.regionaliser.output[self.mask]
        element_raster = self.regionaliser.group.element_raster.values[self.mask]
        subunit_raster = self.regionaliser.group.subunit_raster.values[self.mask]
        function = self._function
        for id_, idx2value in self.id2idx2value.items():
            idx_raster_element = element_raster == id_
            for idx in idx2value:
                idx_raster_subunit = idx_raster_element * (subunit_raster == idx)
                if numpy.any(idx_raster_subunit):
                    idx2value[idx] = function(output[idx_raster_subunit])
                else:
                    idx2value[idx] = float64(numpy.nan)


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
