"""This module imports and defines the static type hints used within HydPy-MPR."""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    cast,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
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


TypeVarParameter = TypeVar("TypeVarParameter", bound=Parameter)


MappingTable: TypeAlias = dict[int64, str]

if TYPE_CHECKING:
    from hydpy_mpr.source import managing

    Tasks: TypeAlias = list[managing.RasterElementTask | managing.RasterSubunitTask]
else:
    Tasks = list

UpscalingFunction: TypeAlias = Callable[[MatrixFloat], float64]

UpscalingOption: TypeAlias = (  # note: synchronise with `constants.py`
    UpscalingFunction | Literal["arithmetic_mean", "geometric_mean", "harmonic_mean"]
)

__all__ = [
    "Any",
    "assert_never",
    "Callable",
    "cast",
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
    "TypeVar",
    "TypeVarParameter",
    "UpscalingOption",
    "UpscalingFunction",
]
