from __future__ import annotations
import dataclasses

import hydpy

from hydpy_mpr.source import calibrating
from hydpy_mpr.source import preprocessing
from hydpy_mpr.source import regionalising
from hydpy_mpr.source import reading
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import utilities
from hydpy_mpr.source import transforming
from hydpy_mpr.source import writing
from hydpy_mpr.source.typing_ import *

TypeVarRasterUpscaler = TypeVar("TypeVarRasterUpscaler", bound=upscaling.RasterUpscaler)
TypeVarRasTransformer = TypeVar(
    "TypeVarRasTransformer", bound=transforming.RasterTransformer[Any]
)


@dataclasses.dataclass(kw_only=True)
class RasterTask(Generic[TypeVarRasterUpscaler, TypeVarRasTransformer]):

    regionaliser: regionalising.RasterRegionaliser
    upscaler: TypeVarRasterUpscaler
    transformers: list[TypeVarRasTransformer]
    hp: hydpy.HydPy = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, raster_groups: reading.RasterGroups) -> None:
        self.hp = hp
        self.regionaliser.activate(raster_groups=raster_groups)
        self.upscaler.activate(regionaliser=self.regionaliser)

    def run(self) -> None:
        self.regionaliser.apply_coefficients()
        self.regionaliser.apply_mask()  # ToDo: remove?
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


@dataclasses.dataclass(kw_only=True)
class MPR:

    mprpath: utilities.NewTypeDataclassDescriptor[str, DirpathMPRData] = (
        utilities.NewTypeDataclassDescriptor()
    )
    hp: hydpy.HydPy
    preprocessors: list[preprocessing.RasterPreprocessor] = dataclasses.field(
        default_factory=lambda: []
    )
    subregionalisers: list[regionalising.RasterSubregionaliser] = dataclasses.field(
        default_factory=lambda: []
    )
    tasks: Tasks
    calibrator: calibrating.Calibrator
    writers: list[writing.Writer] = dataclasses.field(default_factory=lambda: [])

    def __post_init__(self) -> None:
        raster_groups = reading.RasterGroups(mprpath=self.mprpath)
        for preprocessor in self.preprocessors:
            preprocessor.activate(raster_groups=raster_groups)
        for subregionaliser in self.subregionalisers:
            subregionaliser.activate(raster_groups=raster_groups)
        for task in self.tasks:
            task.activate(hp=self.hp, raster_groups=raster_groups)
        self.calibrator.activate(
            hp=self.hp, tasks=self.tasks, subregionalisers=self.subregionalisers
        )
        for writer in self.writers:
            writer.activate(hp=self.hp, calibrator=self.calibrator)

    def run(self) -> None:
        self.calibrator.calibrate()
        for writer in self.writers:
            writer.write()
