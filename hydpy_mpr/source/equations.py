from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import reading
from hydpy_mpr.source import utilities
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Equation(
    Generic[TypeVarProvider, TypeVarDataFloat, TypeVarArrayBool, TypeVarArrayFloat],
    abc.ABC,
):

    source: utilities.NewTypeDataclassDescriptor[str, NameProvider] = (
        utilities.NewTypeDataclassDescriptor()
    )
    name: NameDataset = dataclasses.field(default=NameDataset(""))

    provider: TypeVarProvider = dataclasses.field(init=False)
    mask: TypeVarArrayBool = dataclasses.field(init=False)
    output: TypeVarArrayFloat = dataclasses.field(init=False)

    @property
    @abc.abstractmethod
    def TYPE_DATA_FLOAT(self) -> type[TypeVarDataFloat]:  # pylint: disable=invalid-name
        pass

    @property
    @abc.abstractmethod
    def shape(self) -> int | tuple[int, int]:
        pass

    def activate(self, *, provider: TypeVarProvider) -> None:
        self.provider = provider
        self.mask = numpy.full(self.shape, True, dtype=bool)
        for fieldname, filename in self.name_field2dataset.items():
            rastername = f"data_{fieldname.removeprefix('file_')}"
            raster = provider.name2dataset[filename]  # ToDo: error message
            setattr(self, rastername, raster)  # ToDo: check type?
            self.mask *= raster.mask
        self.output = numpy.full(self.shape, numpy.nan)

    @property
    def inputs(self) -> Mapping[str, TypeVarDataFloat]:
        return {
            name: value
            for field in dataclasses.fields(self)
            if ((name := field.name) != "output")
            and isinstance(value := getattr(self, name), self.TYPE_DATA_FLOAT)
        }

    @property
    def name_field2dataset(self) -> dict[str, NameDataset]:
        return {
            field.name: NameDataset(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if (field.name).startswith("file_")
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
        return self.provider.shape


@dataclasses.dataclass(kw_only=True)
class RasterEquation(
    Equation[reading.RasterGroup, reading.RasterFloat, MatrixBool, MatrixFloat], abc.ABC
):

    TYPE_DATA_FLOAT: ClassVar[type[reading.RasterFloat]] = reading.RasterFloat

    def __post_init__(self) -> None:
        if not self.name:
            self.name = NameDataset(type(self).__qualname__.lower())

    @property
    @override
    def shape(self) -> tuple[int, int]:
        shape = self.provider.shape
        assert isinstance(shape, tuple)
        assert len(shape) == 2
        return shape
