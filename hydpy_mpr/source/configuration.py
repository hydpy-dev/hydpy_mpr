from __future__ import annotations
from dataclasses import dataclass, field

import hydpy

from hydpy_mpr.source import calibration
from hydpy_mpr.source import regionalisation
from hydpy_mpr.source import running
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import transform
from hydpy_mpr.source.typing_ import *


@dataclass
class RasterTask(Generic[TP]):

    equation: regionalisation.RasterEquation
    upscaler: upscaling.RasterUpscaler
    transformers: list[transform.RasterTransformer[TP]]

    def run(self) -> None:
        self.equation.apply_coefficients()
        self.equation.apply_mask()
        self.upscaler.scale_up()
        for transformer in self.transformers:
            transformer.modify_parameters()


@dataclass
class Config(Generic[TP]):

    hp: hydpy.HydPy
    tasks: list[RasterTask[TP]]
    calibrator: calibration.Calibrator
    runner: running.Runner
    subequations: list[regionalisation.RasterEquation] | None = field(
        default_factory=lambda: None
    )

    @property
    def coefficients(self) -> tuple[regionalisation.Coefficient, ...]:
        coefficients: set[regionalisation.Coefficient] = set()
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
