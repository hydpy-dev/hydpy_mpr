from __future__ import annotations
import abc
import dataclasses

import numpy
from scipy import stats

from hydpy_mpr.source import constants
from hydpy_mpr.source import regionalising
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Upscaler(Generic[TypeVarRegionaliser, TypeVarArrayBool], abc.ABC):

    regionaliser: TypeVarRegionaliser = dataclasses.field(init=False)
    mask: TypeVarArrayBool = dataclasses.field(init=False)

    def activate(self, *, regionaliser: TypeVarRegionaliser) -> None:
        self.regionaliser = regionaliser
        self.mask = regionaliser.provider.element_id.mask.copy()
        for raster in regionaliser.inputs.values():
            self.mask *= raster.mask

    @abc.abstractmethod
    def scale_up(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class ElementUpscaler(Upscaler[TypeVarRegionaliser, TypeVarArrayBool], abc.ABC):

    id2value: dict[int64, float64] = dataclasses.field(init=False)

    @override
    def activate(self, *, regionaliser: TypeVarRegionaliser) -> None:
        super().activate(regionaliser=regionaliser)
        self.id2value = {
            id_: float64(numpy.nan) for id_ in self.regionaliser.provider.id2element
        }

    @property
    def name2value(self) -> Mapping[str, float64]:
        id2element = self.regionaliser.provider.id2element
        return {id2element[id_]: value for id_, value in self.id2value.items()}


@dataclasses.dataclass(kw_only=True)
class SubunitUpscaler(Upscaler[TypeVarRegionaliser, TypeVarArrayBool], abc.ABC):

    id2idx2value: dict[int64, dict[int64, float64]] = dataclasses.field(init=False)

    @override
    def activate(self, *, regionaliser: TypeVarRegionaliser) -> None:
        super().activate(regionaliser=regionaliser)

        self.mask *= regionaliser.provider.subunit_id.mask  # ToDo: better error message

        element_raster = regionaliser.provider.element_id.values
        subunit_raster = regionaliser.provider.subunit_id.values
        id2idx2value = {}
        for id_ in regionaliser.provider.id2element:
            idx2value = {}
            idxs = numpy.unique(subunit_raster[numpy.where(element_raster == id_)])
            for idx in sorted(idxs):
                idx2value[int64(idx)] = float64(numpy.nan)
            id2idx2value[id_] = idx2value
        self.id2idx2value = id2idx2value

    @property
    def name2idx2value(self) -> Mapping[str, Mapping[int64, float64]]:
        id2element = self.regionaliser.provider.id2element
        return {id2element[id_]: value for id_, value in self.id2idx2value.items()}


@dataclasses.dataclass(kw_only=True)
class RasterElementUpscaler(
    ElementUpscaler[regionalising.RasterRegionaliser, MatrixBool], abc.ABC
):
    pass


@dataclasses.dataclass(kw_only=True)
class RasterSubunitUpscaler(
    SubunitUpscaler[regionalising.RasterRegionaliser, MatrixBool], abc.ABC
):
    pass


@dataclasses.dataclass(kw_only=True)
class AttributeElementUpscaler(
    ElementUpscaler[regionalising.AttributeRegionaliser, VectorBool], abc.ABC
):
    pass


@dataclasses.dataclass(kw_only=True)
class AttributeSubunitUpscaler(
    SubunitUpscaler[regionalising.AttributeRegionaliser, VectorBool], abc.ABC
):
    pass


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
        group = self.regionaliser.provider
        id_raster = group.element_id.values[self.mask]
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
        element_raster = self.regionaliser.provider.element_id.values[self.mask]
        subunit_raster = self.regionaliser.provider.subunit_id.values[self.mask]
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
