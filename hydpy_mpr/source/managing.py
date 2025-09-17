from __future__ import annotations
import dataclasses
import itertools

import hydpy

from hydpy_mpr.source import calibrating
from hydpy_mpr.source import equations
from hydpy_mpr.source import logging_
from hydpy_mpr.source import preprocessing
from hydpy_mpr.source import regionalising
from hydpy_mpr.source import reading
from hydpy_mpr.source import upscaling
from hydpy_mpr.source import utilities
from hydpy_mpr.source import transforming
from hydpy_mpr.source import writing
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Task(
    Generic[TypeVarProvider, TypeVarRegionaliser, TypeVarUpscaler, TypeVarTransformer]
):

    regionaliser: TypeVarRegionaliser
    upscaler: TypeVarUpscaler
    transformers: Sequence[TypeVarTransformer]
    hp: hydpy.HydPy = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, provider: TypeVarProvider) -> None:
        self.hp = hp
        self.regionaliser.activate(provider=provider)
        self.upscaler.activate(regionaliser=self.regionaliser)
        for transformer in self.transformers:
            transformer.activate(hp=hp, upscaler=self.upscaler)

    @property
    def provider(self) -> NameProvider:
        provider = self.regionaliser.provider
        # ToDo: check source is consistently defined
        return provider

    def run(self) -> None:
        self.regionaliser.apply_coefficients()
        self.regionaliser.apply_mask()  # ToDo: remove?
        self.upscaler.scale_up()
        for transformer in self.transformers:
            transformer.modify_parameters()


class AttributeElementTask(
    Task[
        reading.FeatureClass,
        regionalising.AttributeRegionaliser,
        upscaling.AttributeElementUpscaler,
        transforming.ElementTransformer[Any],
    ]
):
    pass


class AttributeSubunitTask(
    Task[
        reading.FeatureClass,
        regionalising.AttributeRegionaliser,
        upscaling.AttributeSubunitUpscaler,
        transforming.SubunitTransformer[Any],
    ]
):
    pass


class RasterElementTask(
    Task[
        reading.RasterGroup,
        regionalising.RasterRegionaliser,
        upscaling.RasterElementUpscaler,
        transforming.ElementTransformer[Any],
    ]
):
    pass


class RasterSubunitTask(
    Task[
        reading.RasterGroup,
        regionalising.RasterRegionaliser,
        upscaling.RasterSubunitUpscaler,
        transforming.SubunitTransformer[Any],
    ]
):
    pass


@dataclasses.dataclass(kw_only=True)
class MPR:

    mprpath: utilities.NewTypeDataclassDescriptor[str, DirpathMPRData] = (
        utilities.NewTypeDataclassDescriptor()
    )
    hp: hydpy.HydPy
    preprocessors: Sequence[
        preprocessing.AttributePreprocessor | preprocessing.RasterPreprocessor
    ] = dataclasses.field(default_factory=lambda: [])
    subregionalisers: Sequence[
        regionalising.AttributeSubregionaliser | regionalising.RasterSubregionaliser
    ] = dataclasses.field(default_factory=lambda: [])
    tasks: Tasks
    calibrator: calibrating.Calibrator
    loggers: Sequence[logging_.Logger] = dataclasses.field(default_factory=lambda: [])
    writers: Sequence[writing.Writer] = dataclasses.field(default_factory=lambda: [])

    def __post_init__(self) -> None:

        raster_groups = reading.RasterGroups(
            mprpath=self.mprpath,
            equations=tuple(
                itertools.chain(
                    self.raster_preprocessors,
                    self.raster_subregionalisers,
                    (task.regionaliser for task in self.raster_tasks),
                )
            ),
        )
        feature_class = reading.FeatureClasses(
            mprpath=self.mprpath,
            equations=tuple(
                itertools.chain(
                    self.attribute_preprocessors,
                    self.attribute_subregionalisers,
                    (task.regionaliser for task in self.attribute_tasks),
                )
            ),
        )

        for preprocessor in self.preprocessors:
            if isinstance(preprocessor, equations.RasterEquation):
                preprocessor.activate(provider=raster_groups[preprocessor.provider])
            else:
                preprocessor.activate(provider=feature_class[preprocessor.provider])
        for subregionaliser in self.subregionalisers:
            if isinstance(subregionaliser, regionalising.RasterSubregionaliser):
                subregionaliser.activate(
                    provider=raster_groups[subregionaliser.provider]
                )
            else:
                subregionaliser.activate(
                    provider=feature_class[subregionaliser.provider]
                )
        for task in self.tasks:
            if isinstance(task, RasterElementTask | RasterSubunitTask):
                task.activate(hp=self.hp, provider=raster_groups[task.provider])
            else:
                task.activate(hp=self.hp, provider=feature_class[task.provider])
        self.calibrator.activate(
            hp=self.hp,
            tasks=self.tasks,
            subregionalisers=self.subregionalisers,
            loggers=self.loggers,
        )
        for logger in self.loggers:
            logger.activate(hp=self.hp, calibrator=self.calibrator)
        for writer in self.writers:
            writer.activate(hp=self.hp, calibrator=self.calibrator)

    @property
    def attribute_preprocessors(self) -> Sequence[preprocessing.AttributePreprocessor]:
        t = preprocessing.AttributePreprocessor
        return tuple(p for p in self.preprocessors if isinstance(p, t))

    @property
    def raster_preprocessors(self) -> Sequence[preprocessing.RasterPreprocessor]:
        type_ = preprocessing.RasterPreprocessor
        return tuple(p for p in self.preprocessors if isinstance(p, type_))

    @property
    def attribute_subregionalisers(
        self,
    ) -> Sequence[regionalising.AttributeSubregionaliser]:
        type_ = regionalising.AttributeSubregionaliser
        return tuple(p for p in self.subregionalisers if isinstance(p, type_))

    @property
    def raster_subregionalisers(self) -> Sequence[regionalising.RasterSubregionaliser]:
        type_ = regionalising.RasterSubregionaliser
        return tuple(p for p in self.subregionalisers if isinstance(p, type_))

    @property
    def attribute_tasks(self) -> Sequence[AttributeElementTask | AttributeSubunitTask]:
        type_ = (AttributeElementTask, AttributeSubunitTask)
        return tuple(p for p in self.tasks if isinstance(p, type_))

    @property
    def raster_tasks(self) -> Sequence[RasterElementTask | RasterSubunitTask]:
        type_ = (RasterElementTask, RasterSubunitTask)
        return tuple(p for p in self.tasks if isinstance(p, type_))

    def run(self) -> None:
        self.calibrator.calibrate()
        for writer in self.writers:
            writer.write()
