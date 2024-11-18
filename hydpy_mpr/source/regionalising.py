from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import equations
from hydpy_mpr.source.typing_ import *


class Coefficient:

    _value: float

    def __init__(
        self,
        name: str,
        default: float,
        lower: float = -numpy.inf,
        upper: float = numpy.inf,
    ) -> None:
        self.name = name
        self.lower = lower
        self.upper = upper
        self.value = default
        self.default = self.value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float, /) -> None:
        # ToDo: trimming
        self._value = v


@dataclasses.dataclass(kw_only=True)
class RasterRegionaliser(equations.RasterEquation, abc.ABC):

    @property
    def coefficients(self) -> tuple[Coefficient, ...]:
        return tuple(
            value
            for field in dataclasses.fields(self)
            if isinstance(value := getattr(self, field.name), Coefficient)
        )

    @abc.abstractmethod
    def apply_coefficients(self) -> None:
        pass
