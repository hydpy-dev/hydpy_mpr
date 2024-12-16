from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import reading
from hydpy_mpr.source import utilities
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Equation(
    Generic[TypeVarProvider, TypeVarDatasetFloat, TypeVarArrayBool, TypeVarArrayFloat],
    abc.ABC,
):

    provider: utilities.NewTypeDataclassDescriptor[str, NameProvider] = (
        utilities.NewTypeDataclassDescriptor()
    )
    name: NameEquation = dataclasses.field(default=NameEquation(""))

    provider_: TypeVarProvider = dataclasses.field(init=False)
    mask: TypeVarArrayBool = dataclasses.field(init=False)
    output: TypeVarArrayFloat = dataclasses.field(init=False)

    @property
    @abc.abstractmethod
    def TYPE_DATA_FLOAT(  # pylint: disable=invalid-name
        self,
    ) -> type[TypeVarDatasetFloat]:
        pass

    @property
    @abc.abstractmethod
    def shape(self) -> int | tuple[int, int]:
        pass

    def activate(self, *, provider: TypeVarProvider) -> None:
        self.provider_ = provider
        self.mask = numpy.full(self.shape, True, dtype=bool)
        for fieldname_source, datasetname in self.fieldname2datasetname.items():
            fieldname_data = f"dataset_{fieldname_source.removeprefix('source_')}"
            dataset = provider.name2dataset[datasetname]  # ToDo: error message
            setattr(self, fieldname_data, dataset)  # ToDo: check type?
            self.mask *= dataset.mask
        self.output = numpy.full(self.shape, numpy.nan)

    @property
    def inputs(self) -> Mapping[str, TypeVarDatasetFloat]:
        return {
            name: value
            for field in dataclasses.fields(self)
            if ((name := field.name) != "output")
            and isinstance(value := getattr(self, name), self.TYPE_DATA_FLOAT)
        }

    @property
    def fieldname2datasetname(self) -> Mapping[str, NameDataset]:
        return {
            field.name: NameDataset(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if (field.name).startswith("source_")
        }

    def apply_mask(self) -> None:
        self.output[~self.mask] = numpy.nan


@dataclasses.dataclass(kw_only=True)
class AttributeEquation(
    Equation[reading.FeatureClass, reading.AttributeFloat, VectorBool, VectorFloat],
    abc.ABC,
):

    TYPE_DATA_FLOAT: ClassVar[type[reading.AttributeFloat]] = reading.AttributeFloat

    @property
    @override
    def shape(self) -> int:
        return self.provider_.shape


@dataclasses.dataclass(kw_only=True)
class RasterEquation(
    Equation[reading.RasterGroup, reading.RasterFloat, MatrixBool, MatrixFloat], abc.ABC
):

    TYPE_DATA_FLOAT: ClassVar[type[reading.RasterFloat]] = reading.RasterFloat

    def __post_init__(self) -> None:
        if not self.name:
            self.name = NameEquation(type(self).__qualname__.lower())

    @property
    @override
    def shape(self) -> tuple[int, int]:
        shape = self.provider_.shape
        assert isinstance(shape, tuple)
        assert len(shape) == 2
        return shape
