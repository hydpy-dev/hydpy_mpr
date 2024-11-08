from __future__ import annotations
from dataclasses import dataclass, field

import hydpy

from hydpy_mpr.source import calibration
from hydpy_mpr.source import regionalisation
from hydpy_mpr.source import reading
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import transform
from hydpy_mpr.source import writing
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
class MPR:

    hp: hydpy.HydPy
    tasks: list[RasterTask[Any]]
    calibrator: calibration.Calibrator
    writers: list[writing.Writer] = field(default_factory=lambda: [])
    subequations: list[regionalisation.RasterEquation] | None = field(
        default_factory=lambda: None
    )

    def __post_init__(self) -> None:
        raster_groups = reading.read_rastergroups("HydPy-H-Lahn/mpr_data")
        for task in self.tasks:
            task.equation.activate(self, raster_groups=raster_groups)
            task.upscaler.activate(self, task=task)
            for transformer in task.transformers:
                transformer.activate(self, task=task)
        self.calibrator.activate(self)
        for writer in self.writers:
            writer.activate(self)

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

    def run(self) -> None:
        self.calibrator.calibrate()
        for writer in self.writers:
            writer.write()
