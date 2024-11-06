from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields

from numpy import full, inf, nan

from hydpy_mpr.source.reading import Raster, RasterFloat, RasterGroup, RasterGroups
from hydpy_mpr.source.typing_ import Mapping, MatrixFloat


class Coefficient:

    _value: float

    def __init__(
        self, name: str, default: float, lower: float = -inf, upper: float = inf
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


@dataclass
class RasterEquation(ABC):
    """

    >>> from dataclasses import dataclass
    >>> from numpy import asarray
    >>> from hydpy_mpr import MatrixFloat, RasterEquation

    >>> @dataclass
    ... class FC(RasterEquation):
    ...
    ...     data_sand: MatrixFloat
    ...     data_clay: MatrixFloat
    ...
    ...     coef_const: Coefficient
    ...     coef_factor_sand: Coefficient
    ...     coef_factor_clay: Coefficient
    ...
    ...     def apply_coefficients(self) -> None:
    ...         self.output[:] = (
    ...             self.coef_const.value
    ...             + self.coef_factor_sand.value * self.data_sand
    ...             + self.coef_factor_clay.value * self.data_clay
    ...         )

    >>> data_sand = asarray([[0.0, 0.1], [0.2, 0.3], [0.4, 0.5]])
    >>> data_clay = asarray([[0.8, 0.8], [0.5, 0.5], [0.2, 0.2]])


    >>> fc = FC(
    ...     data_sand=asarray([[0.0, 0.1], [0.2, 0.3], [0.4, 0.5]]),
    ...     data_clay=asarray([[0.8, 0.8], [0.5, 0.5], [0.2, 0.2]]),
    ...     coef_const=Coefficient(name="const", default=200.0),
    ...     coef_factor_sand=Coefficient(name="factor_sand", default=0.0),
    ...     coef_factor_clay=Coefficient(name="factor_clay", default=0.0),
    ... )

    >>> fc.apply_coefficients()
    >>> fc.output
    array([[200., 200.],
           [200., 200.],
           [200., 200.]])

    >>> fc.coef_const.value = 200.0
    >>> fc.coef_factor_sand.value = -100.0
    >>> fc.coef_factor_clay.value = 300.0

    >>> fc.apply_coefficients()
    >>> fc.output
    array([[440., 430.],
           [330., 320.],
           [220., 210.]])
    """

    dir_group: str
    _group: RasterGroup | None = field(init=False, default_factory=lambda: None)
    output: MatrixFloat = field(init=False)

    def extract_rasters(self, raster_groups: RasterGroups) -> None:
        group = raster_groups[self.dir_group]
        self._group = group
        self.mask = full(self.shape, True, dtype=bool)
        for fieldname, filename in self.fieldname2filename.items():
            rastername = f"data_{fieldname.removeprefix('file_')}"
            raster = group.data_rasters[filename]
            setattr(self, rastername, raster)
            self.mask *= raster.mask
        self.output = full(self.shape, nan)

    @property
    def group(self) -> RasterGroup:
        if (group := self._group) is None:
            raise RuntimeError
        return group

    @property
    def shape(self) -> tuple[int, int]:
        shape = self.group.shape
        assert isinstance(shape, tuple)
        assert len(shape) == 2
        return shape

    @property
    def fieldname2filename(self) -> dict[str, str]:
        return {
            field_.name: getattr(self, field_.name)
            for field_ in fields(self)
            if (field_.name).startswith("file_")
        }

    @property
    def inputs(self) -> Mapping[str, RasterFloat]:
        return {
            name: value
            for field_ in fields(self)
            if ((name := field_.name) != "output")
            and isinstance(value := getattr(self, name), Raster)
        }

    @property
    def coefficients(self) -> tuple[Coefficient, ...]:
        return tuple(
            value
            for field_ in fields(self)
            if isinstance(value := getattr(self, field_.name), Coefficient)
        )

    @abstractmethod
    def apply_coefficients(self) -> None:
        pass

    def apply_mask(self) -> None:
        self.output[~self.mask] = nan
