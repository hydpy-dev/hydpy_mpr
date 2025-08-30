"""This module imports and defines the static type hints used within HydPy-MPR."""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    cast,
    ClassVar,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    NewType,
    NoReturn,
    overload,
    Protocol,
    Sequence,
    TypeAlias,
    TYPE_CHECKING,
    TypeVar,
)

from hydpy.core.parametertools import Parameter
from hydpy.core.typingtools import (
    Matrix,
    MatrixBool,
    MatrixFloat,
    MatrixInt,
    Vector,
    VectorBool,
    VectorFloat,
    VectorInt,
)
from numpy import int64, float64
from typing_extensions import assert_never, override, Self


# type variables

TypeVarArrayBool = TypeVar("TypeVarArrayBool", VectorBool, MatrixBool)
TypeVarArrayFloat = TypeVar("TypeVarArrayFloat", VectorFloat, MatrixFloat)
TypeVarParameter = TypeVar("TypeVarParameter", bound=Parameter)

if TYPE_CHECKING:
    from hydpy_mpr.source import equations
    from hydpy_mpr.source import reading
    from hydpy_mpr.source import regionalising
    from hydpy_mpr.source import transforming
    from hydpy_mpr.source import upscaling

    TypeVarProvider = TypeVar("TypeVarProvider", bound=reading.Provider[Any, Any])
    TypeVarEquation = TypeVar(
        "TypeVarEquation", bound=equations.Equation[Any, Any, Any, Any]
    )
    TypeVarDataset = TypeVar(
        "TypeVarDataset",
        reading.AttributeInt | reading.AttributeFloat,
        reading.RasterInt | reading.RasterFloat,
    )
    TypeVarDatasetInt = TypeVar(
        "TypeVarDatasetInt", reading.AttributeInt, reading.RasterInt
    )
    TypeVarDatasetFloat = TypeVar(
        "TypeVarDatasetFloat", reading.AttributeFloat, reading.RasterFloat
    )
    TypeVarRegionaliser = TypeVar(
        "TypeVarRegionaliser", bound=regionalising.Regionaliser[Any, Any, Any, Any]
    )
    TypeVarUpscaler = TypeVar("TypeVarUpscaler", bound=upscaling.Upscaler[Any, Any])
    TypeVarTransformer = TypeVar(
        "TypeVarTransformer", bound=transforming.Transformer[Any, Any]
    )
else:
    TypeVarProvider = TypeVar("TypeVarProvider")
    TypeVarEquation = TypeVar("TypeVarEquation")
    TypeVarDataset = TypeVar("TypeVarDataset")
    TypeVarDatasetInt = TypeVar("TypeVarDatasetInt")
    TypeVarDatasetFloat = TypeVar("TypeVarDatasetFloat")
    TypeVarRegionaliser = TypeVar("TypeVarRegionaliser")
    TypeVarUpscaler = TypeVar("TypeVarUpscaler")
    TypeVarTransformer = TypeVar("TypeVarTransformer")


# protocols


class AttributeUpscalingFunction(Protocol):
    def __call__(self, values: VectorFloat, /, *, weights: VectorFloat) -> float64: ...


class RasterUpscalingFunction(Protocol):
    def __call__(self, values: MatrixFloat, /) -> float64: ...


# type aliases

AttributeUpscalingOption: TypeAlias = (  # note: synchronise with `constants.py`
    AttributeUpscalingFunction
    | Literal["arithmetic_mean", "geometric_mean", "harmonic_mean"]
)
RasterUpscalingOption: TypeAlias = (  # note: synchronise with `constants.py`
    RasterUpscalingFunction
    | Literal["arithmetic_mean", "geometric_mean", "harmonic_mean"]
)

MappingTable: TypeAlias = Mapping[int64, str]
"""Table for mapping element IDs to element names required when working with raster 
files (the items must be added in sorted order, so that iteration also progresses in 
sorted order)."""

if TYPE_CHECKING:
    from hydpy_mpr.source import managing

    Tasks: TypeAlias = Sequence[
        managing.AttributeElementTask
        | managing.AttributeSubunitTask
        | managing.RasterElementTask
        | managing.RasterSubunitTask
    ]
else:
    Tasks = Sequence


# new types

DirpathMPRData = NewType("DirpathMPRData", str)
FilepathGeopackage = NewType("FilepathGeopackage", str)
NameProvider = NewType("NameProvider", str)
NameEquation = NewType("NameEquation", str)
NameDataset = NewType("NameDataset", str)


__all__ = [
    "Any",
    "assert_never",
    "AttributeUpscalingFunction",
    "AttributeUpscalingOption",
    "Callable",
    "cast",
    "ClassVar",
    "DirpathMPRData",
    "FilepathGeopackage",
    "float64",
    "Generic",
    "int64",
    "Iterable",
    "Iterator",
    "Literal",
    "Matrix",
    "Mapping",
    "MappingTable",
    "MatrixBool",
    "MatrixFloat",
    "MatrixInt",
    "NameDataset",
    "NameEquation",
    "NameProvider",
    "NoReturn",
    "overload",
    "override",
    "Vector",
    "VectorBool",
    "VectorFloat",
    "VectorInt",
    "RasterUpscalingFunction",
    "RasterUpscalingOption",
    "Self",
    "Sequence",
    "Tasks",
    "TypeAlias",
    "TYPE_CHECKING",
    "TypeVar",
    "TypeVarArrayBool",
    "TypeVarArrayFloat",
    "TypeVarDataset",
    "TypeVarDatasetFloat",
    "TypeVarDatasetInt",
    "TypeVarEquation",
    "TypeVarParameter",
    "TypeVarProvider",
    "TypeVarRegionaliser",
    "TypeVarUpscaler",
    "TypeVarTransformer",
]
