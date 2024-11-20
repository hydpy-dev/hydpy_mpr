from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import equations
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True, eq=False)
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


@dataclasses.dataclass(kw_only=True)
class RasterSubregionaliser(RasterRegionaliser, abc.ABC):

    name: str

    @override
    def activate(self, *, raster_groups: reading.RasterGroups) -> None:
        super().activate(raster_groups=raster_groups)
        self.mask[:, :] = True
        for input_ in self.inputs.values():
            self.mask *= input_.mask
        raster = reading.RasterFloat(  # pylint: disable=unexpected-keyword-arg
            values=self.output
        )
        raster.mask = self.mask.copy()
        self.group.data_rasters[self.name] = raster
