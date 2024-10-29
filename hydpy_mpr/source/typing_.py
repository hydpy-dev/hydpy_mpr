"""This module imports and defines the static type hints used within HydPy-MPR."""

from typing import (
    Callable,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    overload,
    TypeAlias,
    TypeVar,
)

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
from numpy import int64


MappingTable: TypeAlias = dict[int64, str]

__all__ = [
    "assert_never",
    "Callable",
    "Generic",
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
    "TypeAlias",
    "TypeVar",
]
