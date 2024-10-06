"""This module imports and defines the static type hints used within HydPy-MPR."""

from typing import TypeAlias, Callable, Literal

MappingTable: TypeAlias = dict[int, str]

__all__ = ["Callable", "Literal"]
