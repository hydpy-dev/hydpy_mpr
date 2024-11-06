from __future__ import annotations
from dataclasses import dataclass, field

from hydpy_mpr.source.calibration import Calibrator
from hydpy_mpr.source.regionalisation import Coefficient, RasterEquation
from hydpy_mpr.source.upscaling import RasterUpscaler
from hydpy_mpr.source.transform import RasterTransformer, TP
from hydpy_mpr.source.typing_ import Generic


@dataclass
class RasterTask(Generic[TP]):

    equation: RasterEquation
    upscaler: RasterUpscaler
    transformers: list[RasterTransformer[TP]]

    def run(self) -> None:
        self.equation.apply_coefficients()
        self.equation.apply_mask()
        self.upscaler.scale_up()
        for transformer in self.transformers:
            transformer.modify_parameters()


@dataclass
class Config(Generic[TP]):

    calibrator: Calibrator
    tasks: list[RasterTask[TP]]
    subequations: list[RasterEquation] | None = field(default_factory=lambda: None)

    @property
    def coefficients(self) -> tuple[Coefficient, ...]:
        coefficients: set[Coefficient] = set()
        for task in self.tasks:
            coefficients.update(task.equation.coefficients)
        return tuple(sorted(coefficients, key=lambda c: c.name))

    @property
    def lowers(self) -> tuple[float, ...]:
        return tuple(c.lower for c in self.coefficients)

    @property
    def uppers(self) -> tuple[float, ...]:
        return tuple(c.upper for c in self.coefficients)

    @property
    def values(self) -> tuple[float, ...]:
        return tuple(c.value for c in self.coefficients)
