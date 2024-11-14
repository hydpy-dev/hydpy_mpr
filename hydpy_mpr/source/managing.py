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

TypeVarRasterUpscaler = TypeVar("TypeVarRasterUpscaler", bound=upscaling.RasterUpscaler)
TypeVarRasTransformer = TypeVar(
    "TypeVarRasTransformer", bound=transforming.RasterTransformer[Any]
)


@dataclasses.dataclass
class RasterTask(Generic[TypeVarRasterUpscaler, TypeVarRasTransformer]):

    equation: regionalising.RasterEquation
    upscaler: TypeVarRasterUpscaler
    transformers: list[TypeVarRasTransformer]
    hp: hydpy.HydPy = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, raster_groups: reading.RasterGroups) -> None:
        self.hp = hp
        self.equation.activate(raster_groups=raster_groups)
        self.upscaler.activate(equation=self.equation)

    def run(self) -> None:
        self.equation.apply_coefficients()
        self.equation.apply_mask()
        self.upscaler.scale_up()
        for transformer in self.transformers:
            transformer.modify_parameters()


class RasterElementTask(
    RasterTask[
        upscaling.RasterElementUpscaler, transforming.RasterElementTransformer[Any]
    ]
):

    @override
    def activate(self, *, hp: hydpy.HydPy, raster_groups: reading.RasterGroups) -> None:
        super().activate(hp=hp, raster_groups=raster_groups)
        for transformer in self.transformers:
            transformer.activate(hp=hp, upscaler=self.upscaler)


class RasterSubunitTask(
    RasterTask[
        upscaling.RasterSubunitUpscaler, transforming.RasterSubunitTransformer[Any]
    ]
):

    @override
    def activate(self, *, hp: hydpy.HydPy, raster_groups: reading.RasterGroups) -> None:
        super().activate(hp=hp, raster_groups=raster_groups)
        for transformer in self.transformers:
            transformer.activate(hp=hp, upscaler=self.upscaler)


@dataclasses.dataclass
class MPR:

    mprpath: str
    hp: hydpy.HydPy
    tasks: Tasks
    calibrator: calibrating.Calibrator
    writers: list[writing.Writer] = dataclasses.field(default_factory=lambda: [])
    subequations: list[regionalising.RasterEquation] | None = dataclasses.field(
        default_factory=lambda: None
    )

    def __post_init__(self) -> None:
        raster_groups = reading.RasterGroups(self.mprpath)
        for task in self.tasks:
            task.activate(hp=self.hp, raster_groups=raster_groups)
        self.calibrator.activate(hp=self.hp, tasks=self.tasks)
        for writer in self.writers:
            writer.activate(hp=self.hp, calibrator=self.calibrator)

    def run(self) -> None:
        self.calibrator.calibrate()
        for writer in self.writers:
            writer.write()
