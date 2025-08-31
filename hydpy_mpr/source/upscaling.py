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
        self.mask = regionaliser.provider_.element_id.mask.copy()
        for dataset in regionaliser.inputs.values():
            self.mask *= dataset.mask

    @abc.abstractmethod
    def scale_up(self) -> None:
        pass

    def _prepare_uniques_and_idxs(self, ids: VectorInt) -> tuple[VectorInt, MatrixInt]:
        argsort_ids = numpy.argsort(ids)
        sorted_ids = ids[argsort_ids]
        unique_ids, unique_index, unique_counts = numpy.unique(
            sorted_ids, return_index=True, return_counts=True
        )
        splitted_sorted_ids = numpy.split(argsort_ids, unique_index[1:])
        idxs = numpy.full(
            (unique_ids.shape[0], numpy.max(unique_counts)), -1, dtype=int64
        )
        for i, (count, subidxs) in enumerate(zip(unique_counts, splitted_sorted_ids)):
            idxs[i, :count] = subidxs
        return unique_ids, idxs


@dataclasses.dataclass(kw_only=True)
class ElementUpscaler(Upscaler[TypeVarRegionaliser, TypeVarArrayBool], abc.ABC):

    id2value: dict[int64, float64] = dataclasses.field(init=False)
    _uniques: VectorInt = dataclasses.field(init=False)

    @override
    def activate(self, *, regionaliser: TypeVarRegionaliser) -> None:
        super().activate(regionaliser=regionaliser)
        self.id2value = {
            id_: float64(numpy.nan) for id_ in self.regionaliser.provider_.id2element
        }
        self._uniques, self._idxs = self._prepare_uniques_and_idxs(
            regionaliser.provider_.element_id.values[self.mask]
        )

    @property
    def name2value(self) -> Mapping[str, float64]:
        id2element = self.regionaliser.provider_.id2element
        return {id2element[id_]: value for id_, value in self.id2value.items()}


@dataclasses.dataclass(kw_only=True)
class SubunitUpscaler(Upscaler[TypeVarRegionaliser, TypeVarArrayBool], abc.ABC):

    id2idx2value: dict[int64, dict[int64, float64]] = dataclasses.field(init=False)
    _uniques: VectorInt = dataclasses.field(init=False)
    _idxs: MatrixInt = dataclasses.field(init=False)
    _splits: dict[int64, tuple[int64, int64]] = dataclasses.field(init=False)

    @override
    def activate(self, *, regionaliser: TypeVarRegionaliser) -> None:
        super().activate(regionaliser=regionaliser)

        self.mask *= (
            regionaliser.provider_.subunit_id.mask
        )  # ToDo: better error message

        element_id = regionaliser.provider_.element_id.values
        subunit_id = regionaliser.provider_.subunit_id.values
        id2idx2value = {}
        for id_ in regionaliser.provider_.id2element:
            idx2value = {}
            idxs = numpy.unique(subunit_id[numpy.where(element_id == id_)])
            for idx in sorted(idxs):
                idx2value[int64(idx)] = float64(numpy.nan)
            id2idx2value[id_] = idx2value
        self.id2idx2value = id2idx2value

        element_ids = element_id[self.mask]
        subunit_ids = subunit_id[self.mask]
        factor = 10 ** int64(numpy.ceil(numpy.log10(numpy.max(subunit_ids)) + 1.0))
        combined_ids = factor * element_ids + subunit_ids
        self._splits = dict(zip(combined_ids, zip(element_ids, subunit_ids)))
        self._uniques, self._idxs = self._prepare_uniques_and_idxs(combined_ids)

    @property
    def name2idx2value(self) -> Mapping[str, Mapping[int64, float64]]:
        id2element = self.regionaliser.provider_.id2element
        return {id2element[id_]: value for id_, value in self.id2idx2value.items()}


@dataclasses.dataclass(kw_only=True)
class AttributeUpscaler(
    Upscaler[regionalising.AttributeRegionaliser, VectorBool], abc.ABC
):
    pass


@dataclasses.dataclass(kw_only=True)
class RasterUpscaler(Upscaler[regionalising.RasterRegionaliser, MatrixBool], abc.ABC):
    pass


@dataclasses.dataclass(kw_only=True)
class RasterElementUpscaler(
    RasterUpscaler,
    ElementUpscaler[regionalising.RasterRegionaliser, MatrixBool],
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True)
class RasterSubunitUpscaler(
    RasterUpscaler,
    SubunitUpscaler[regionalising.RasterRegionaliser, MatrixBool],
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True)
class AttributeElementUpscaler(
    AttributeUpscaler,
    ElementUpscaler[regionalising.AttributeRegionaliser, VectorBool],
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True)
class AttributeSubunitUpscaler(
    AttributeUpscaler,
    SubunitUpscaler[regionalising.AttributeRegionaliser, VectorBool],
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True)
class AttributeDefaultUpscaler(AttributeUpscaler):
    function: AttributeUpscalingOption = constants.UP_A
    _function: AttributeUpscalingFunction = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._function = self._query_function(self.function)

    @staticmethod
    def _query_function(
        function: AttributeUpscalingOption,
    ) -> AttributeUpscalingFunction:
        match function:
            case constants.UP_A:
                return numpy.average
            case constants.UP_H:
                return stats.hmean  # type: ignore[no-any-return]
            case constants.UP_G:
                return stats.gmean  # type: ignore[no-any-return]
            case _:
                return function


@dataclasses.dataclass(kw_only=True)
class RasterDefaultUpscaler(RasterUpscaler):
    function: RasterUpscalingOption = constants.UP_A
    _function: RasterUpscalingFunction = dataclasses.field(init=False)
    _idxs: MatrixInt = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self._function = self._query_function(self.function)

    @staticmethod
    def _query_function(function: RasterUpscalingOption) -> RasterUpscalingFunction:
        match function:
            case constants.UP_A:
                return lambda x: numpy.nanmean(x, axis=1, keepdims=True)
            case constants.UP_H:
                return lambda x: stats.hmean(
                    x, axis=1, nan_policy="omit", keepdims=True
                )
            case constants.UP_G:
                return lambda x: stats.gmean(
                    x, axis=1, nan_policy="omit", keepdims=True
                )
            case _:
                return function

    def _apply_function(self) -> VectorFloat:
        output = self.regionaliser.output[self.mask]
        output = numpy.concatenate((output, numpy.array([numpy.nan])))
        results = self._function(output[self._idxs])
        output[-1] = 0.0
        missing = numpy.any(numpy.isnan(output[self._idxs]), axis=1)
        results[missing] = numpy.nan
        return results


@dataclasses.dataclass(kw_only=True)
class AttributeElementDefaultUpscaler(
    AttributeDefaultUpscaler, AttributeElementUpscaler
):

    @override
    def scale_up(self) -> None:
        id2value = self.id2value
        output = self.regionaliser.output[self.mask]
        provider = self.regionaliser.provider_
        ids = provider.element_id.values[self.mask]
        weights = provider.size.values[self.mask]
        function = self._function
        for id_ in id2value:
            idxs = id_ == ids
            if numpy.any(idxs):
                id2value[id_] = function(output[idxs], weights=weights)
            else:
                id2value[id_] = float64(numpy.nan)


@dataclasses.dataclass(kw_only=True)
class RasterElementDefaultUpscaler(RasterDefaultUpscaler, RasterElementUpscaler):

    @override
    def scale_up(self) -> None:
        id2value = self.id2value
        for id_, result in zip(self._uniques, self._apply_function()):
            id2value[id_] = result


@dataclasses.dataclass(kw_only=True)
class AttributeSubunitDefaultUpscaler(
    AttributeDefaultUpscaler, AttributeSubunitUpscaler
):

    @override
    def scale_up(self) -> None:
        output = self.regionaliser.output[self.mask]
        provider = self.regionaliser.provider_
        element_id = provider.element_id.values[self.mask]
        subunit_id = provider.subunit_id.values[self.mask]
        weights = provider.subunit_id.values[self.mask]
        function = self._function
        for id_, idx2value in self.id2idx2value.items():
            idx_element = element_id == id_
            for idx in idx2value:
                idx_subunit = idx_element * (subunit_id == idx)
                if numpy.any(idx_subunit):
                    idx2value[idx] = function(
                        output[idx_subunit], weights=weights[idx_subunit]
                    )
                else:
                    idx2value[idx] = float64(numpy.nan)


@dataclasses.dataclass(kw_only=True)
class RasterSubunitDefaultUpscaler(RasterDefaultUpscaler, RasterSubunitUpscaler):

    @override
    def scale_up(self) -> None:
        splits = self._splits
        id2idx2value = self.id2idx2value
        for unique, result in zip(self._uniques, self._apply_function()):
            id_element, idx_subunit = splits[unique]
            id2idx2value[id_element][idx_subunit] = result
