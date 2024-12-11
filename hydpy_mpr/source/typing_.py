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
    TypeVarData = TypeVar(
        "TypeVarData",
        reading.AttributeInt | reading.AttributeFloat,
        reading.RasterInt | reading.RasterFloat,
    )
    TypeVarDataInt = TypeVar("TypeVarDataInt", reading.AttributeInt, reading.RasterInt)
    TypeVarDataFloat = TypeVar(
        "TypeVarDataFloat", reading.AttributeFloat, reading.RasterFloat
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
    TypeVarData = TypeVar("TypeVarData")
    TypeVarDataInt = TypeVar("TypeVarDataInt")
    TypeVarDataFloat = TypeVar("TypeVarDataFloat")
    TypeVarRegionaliser = TypeVar("TypeVarRegionaliser")
    TypeVarUpscaler = TypeVar("TypeVarUpscaler")
    TypeVarTransformer = TypeVar("TypeVarTransformer")

# type aliases

MappingTable: TypeAlias = dict[int64, str]

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

UpscalingFunction: TypeAlias = Callable[[MatrixFloat], float64]

UpscalingOption: TypeAlias = (  # note: synchronise with `constants.py`
    UpscalingFunction | Literal["arithmetic_mean", "geometric_mean", "harmonic_mean"]
)


# new types

DirpathMPRData = NewType("DirpathMPRData", str)
FilepathGeopackage = NewType("FilepathGeopackage", str)
NameProvider = NewType("NameProvider", str)
NameDataset = NewType("NameDataset", str)


__all__ = [
    "Any",
    "assert_never",
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
    "NameProvider",
    "NameDataset",
    "NoReturn",
    "overload",
    "override",
    "Vector",
    "VectorBool",
    "VectorFloat",
    "VectorInt",
    "Self",
    "Sequence",
    "Tasks",
    "TypeAlias",
    "TYPE_CHECKING",
    "TypeVar",
    "TypeVarArrayBool",
    "TypeVarArrayFloat",
    "TypeVarData",
    "TypeVarDataFloat",
    "TypeVarDataInt",
    "TypeVarEquation",
    "TypeVarParameter",
    "TypeVarProvider",
    "TypeVarRegionaliser",
    "TypeVarUpscaler",
    "TypeVarTransformer",
    "UpscalingOption",
    "UpscalingFunction",
]
