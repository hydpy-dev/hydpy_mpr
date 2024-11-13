from __future__ import annotations
import abc
import dataclasses

import hydpy
import numpy

from hydpy_mpr.source import managing
from hydpy_mpr.source import upscaling
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass
class RasterTransformer(abc.ABC, Generic[TP]):

    parameter: type[TP]
    model: str | None = dataclasses.field(default_factory=lambda: None)
    selection: hydpy.Selection | None = dataclasses.field(default_factory=lambda: None)
    hp: hydpy.HydPy = dataclasses.field(init=False)
    element2parameter: dict[str, TP] = dataclasses.field(init=False)
    task: managing.RasterTask[TP] = dataclasses.field(init=False)
    mpr: managing.MPR = dataclasses.field(init=False)

    def activate(
        self, mpr: managing.MPR, /, *, task: managing.RasterTask[TP], hp: hydpy.HydPy
    ) -> None:
        self.mpr = mpr
        self.task = task
        self.hp = hp
        if self.selection is None:
            elements = hp.elements
        else:
            elements = self.selection.elements
        element2parameter = {}
        for element in elements:
            if self.model in (element.model.name, None):
                parameter = element.model.parameters.control[self.parameter.name]
                assert isinstance(parameter, self.parameter)
                element2parameter[element.name] = parameter
        self.element2parameter = element2parameter

    @abc.abstractmethod
    def modify_parameters(self) -> None:
        pass


@dataclasses.dataclass
class RasterElementTransformer(RasterTransformer[TP], abc.ABC):

    upscaler: upscaling.RasterElementUpscaler = dataclasses.field(init=False)

    @override
    def activate(
        self, mpr: managing.MPR, /, *, task: managing.RasterTask[TP], hp: hydpy.HydPy
    ) -> None:
        super().activate(mpr, task=task, hp=hp)
        assert isinstance(task.upscaler, upscaling.RasterElementUpscaler)
        self.upscaler = task.upscaler

    @override
    def modify_parameters(self) -> None:
        element2parameter = self.element2parameter
        for name, value in self.upscaler.name2value.items():
            if (parameter := element2parameter.get(name)) is not None:
                self.modify_parameter(parameter=parameter, value=value)

    @abc.abstractmethod
    def modify_parameter(self, parameter: TP, value: float64) -> None:
        pass


@dataclasses.dataclass
class RasterSubunitTransformer(RasterTransformer[TP], abc.ABC):
    upscaler: upscaling.RasterSubunitUpscaler = dataclasses.field(init=False)

    @override
    def activate(
        self, mpr: managing.MPR, /, *, task: managing.RasterTask[TP], hp: hydpy.HydPy
    ) -> None:
        super().activate(mpr, task=task, hp=hp)
        assert isinstance(task.upscaler, upscaling.RasterSubunitUpscaler)
        self.upscaler = task.upscaler

    @override
    def modify_parameters(self) -> None:
        element2parameter = self.element2parameter
        for name, value in self.upscaler.name2idx2value.items():
            if (parameter := element2parameter.get(name)) is not None:
                self.modify_parameter(parameter=parameter, values=value)

    @abc.abstractmethod
    def modify_parameter(self, parameter: TP, values: dict[int64, float64]) -> None:
        pass


class RasterElementIdentityTransformer(RasterElementTransformer[TP]):

    @override
    def modify_parameter(self, parameter: TP, value: float64) -> None:
        # ToDo: parameterstep
        if not numpy.isnan(value):
            parameter(value)


class RasterSubunitIdentityTransformer(RasterSubunitTransformer[TP]):

    @override
    def modify_parameter(self, parameter: TP, values: dict[int64, float64]) -> None:
        # ToDo: parameterstep
        for idx, value in values.items():
            if not numpy.isnan(value):
                parameter.values[idx] = value
