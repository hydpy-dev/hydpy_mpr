from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import equations
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True, repr=False, eq=False)
class Coefficient:

    name: str
    default: float
    lower: float = dataclasses.field(default=-numpy.inf)
    upper: float = dataclasses.field(default=numpy.inf)
    _value: float = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.value = self.default
        self.default = self.value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float, /) -> None:
        # ToDo: trimming
        self._value = v


@dataclasses.dataclass(kw_only=True, repr=False)
class Regionaliser(
    equations.Equation[
        TypeVarProvider, TypeVarDatasetFloat, TypeVarArrayBool, TypeVarArrayFloat
    ],
    abc.ABC,
):
    @property
    def coefficients(self) -> Sequence[Coefficient]:
        return tuple(
            value
            for field in dataclasses.fields(self)
            if isinstance(value := getattr(self, field.name), Coefficient)
        )

    @abc.abstractmethod
    def apply_coefficients(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True, repr=False)
class RasterRegionaliser(
    Regionaliser[reading.RasterGroup, reading.RasterFloat, MatrixBool, MatrixFloat],
    equations.RasterEquation,
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True, repr=False)
class AttributeRegionaliser(
    Regionaliser[reading.FeatureClass, reading.AttributeFloat, VectorBool, VectorFloat],
    equations.AttributeEquation,
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True, repr=False)
class Subregionaliser(
    Regionaliser[
        TypeVarProvider, TypeVarDatasetFloat, TypeVarArrayBool, TypeVarArrayFloat
    ],
    abc.ABC,
):
    @override
    def activate(self, *, provider: TypeVarProvider) -> None:
        super().activate(provider=provider)
        self.mask[:, :] = True
        for input_ in self.inputs.values():
            self.mask *= input_.mask
        raster = reading.RasterFloat(values=self.output)
        raster.mask = self.mask.copy()
        self.provider_.name2dataset[NameDataset(self.name)] = raster


@dataclasses.dataclass(kw_only=True, repr=False)
class AttributeSubregionaliser(
    Subregionaliser[
        reading.FeatureClass, reading.AttributeFloat, VectorBool, VectorFloat
    ],
    AttributeRegionaliser,
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True, repr=False)
class RasterSubregionaliser(
    Subregionaliser[reading.RasterGroup, reading.RasterFloat, MatrixBool, MatrixFloat],
    RasterRegionaliser,
    abc.ABC,
):
    pass
