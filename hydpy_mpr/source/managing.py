from __future__ import annotations
import dataclasses

import hydpy

from hydpy_mpr.source import calibrating
from hydpy_mpr.source import regionalising
from hydpy_mpr.source import reading
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import transforming
from hydpy_mpr.source import writing
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass
class RasterTask(Generic[TP]):

    mpr: MPR = dataclasses.field(init=False)
    equation: regionalising.RasterEquation
    upscaler: upscaling.RasterElementUpscaler | upscaling.RasterSubunitUpscaler
    transformers: list[transforming.RasterTransformer[TP]]
    mask: MatrixBool = dataclasses.field(init=False)

    def activate(self, mpr: MPR, /, raster_groups: reading.RasterGroups) -> None:
        self.mpr = mpr
        self.equation.activate(self.mpr, raster_groups=raster_groups)
        self.upscaler.activate(self.mpr, task=self)
        for transformer in self.transformers:
            transformer.activate(self.mpr, task=self)

        group = self.equation.group
        self.mask = group.element_raster.mask.copy()
        if isinstance(self.upscaler, upscaling.RasterSubunitUpscaler):
            self.mask *= group.subunit_raster.mask  # ToDo: better error message
        for raster in self.equation.inputs.values():
            self.mask *= raster.mask

    def run(self) -> None:
        self.equation.apply_coefficients()
        self.equation.apply_mask()
        self.upscaler.scale_up()
        for transformer in self.transformers:
            transformer.modify_parameters()


@dataclasses.dataclass
class MPR:

    mprpath: str
    hp: hydpy.HydPy
    tasks: list[RasterTask[Any]]
    calibrator: calibrating.Calibrator
    writers: list[writing.Writer] = dataclasses.field(default_factory=lambda: [])
    subequations: list[regionalising.RasterEquation] | None = dataclasses.field(
        default_factory=lambda: None
    )

    def __post_init__(self) -> None:
        raster_groups = reading.RasterGroups(self.mprpath)
        for task in self.tasks:
            task.activate(self, raster_groups=raster_groups)
        self.calibrator.activate(self)
        for writer in self.writers:
            writer.activate(self)

    @property
    def coefficients(self) -> tuple[regionalising.Coefficient, ...]:
        coefficients: set[regionalising.Coefficient] = set()
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
