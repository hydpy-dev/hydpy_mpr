"""This module imports and defines the static type hints used within HydPy-MPR."""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    overload,
    Sequence,
    TypeAlias,
    TypeVar,
)

from hydpy.core.parametertools import Parameter
from typing_extensions import assert_never, Self

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


MappingTable: TypeAlias = dict[int64, str]

TP = TypeVar("TP", bound=Parameter)


__all__ = [
    "Any",
    "assert_never",
    "Callable",
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
    "overload",
    "Vector",
    "VectorBool",
    "VectorFloat",
    "VectorInt",
    "Self",
    "Sequence",
    "TP",
    "TypeAlias",
    "TypeVar",
]
