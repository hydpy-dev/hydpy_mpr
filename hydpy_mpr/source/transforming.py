from __future__ import annotations
import abc
import dataclasses

import hydpy
import numpy

from hydpy_mpr.source import upscaling
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class RasterTransformer(abc.ABC, Generic[TypeVarRasterUpscaler, TypeVarParameter]):

    parameter: type[TypeVarParameter]
    model: str | None = dataclasses.field(default_factory=lambda: None)
    selection: hydpy.Selection | None = dataclasses.field(default_factory=lambda: None)
    hp: hydpy.HydPy = dataclasses.field(init=False)
    element2parameter: dict[str, TypeVarParameter] = dataclasses.field(init=False)

    @abc.abstractmethod
    def activate(self, *, hp: hydpy.HydPy, upscaler: TypeVarRasterUpscaler) -> None:
        pass

    def _activate(self, hp: hydpy.HydPy) -> None:
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


@dataclasses.dataclass(kw_only=True)
class RasterElementTransformer(
    RasterTransformer[upscaling.RasterElementUpscaler, TypeVarParameter], abc.ABC
):

    upscaler: upscaling.RasterElementUpscaler = dataclasses.field(init=False)

    @override
    def activate(
        self, *, hp: hydpy.HydPy, upscaler: upscaling.RasterElementUpscaler
    ) -> None:
        super()._activate(hp=hp)
        self.upscaler = upscaler

    @override
    def modify_parameters(self) -> None:
        element2parameter = self.element2parameter
        for name, value in self.upscaler.name2value.items():
            if (parameter := element2parameter.get(name)) is not None:
                self.modify_parameter(parameter=parameter, value=value)

    @abc.abstractmethod
    def modify_parameter(self, parameter: TypeVarParameter, value: float64) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class RasterSubunitTransformer(
    RasterTransformer[upscaling.RasterSubunitUpscaler, TypeVarParameter], abc.ABC
):
    upscaler: upscaling.RasterSubunitUpscaler = dataclasses.field(init=False)

    @override
    def activate(
        self, *, hp: hydpy.HydPy, upscaler: upscaling.RasterSubunitUpscaler
    ) -> None:
        super()._activate(hp=hp)
        self.upscaler = upscaler

    @override
    def modify_parameters(self) -> None:
        element2parameter = self.element2parameter
        for name, value in self.upscaler.name2idx2value.items():
            if (parameter := element2parameter.get(name)) is not None:
                self.modify_parameter(parameter=parameter, values=value)

    @abc.abstractmethod
    def modify_parameter(
        self, parameter: TypeVarParameter, values: dict[int64, float64]
    ) -> None:
        pass


class RasterElementIdentityTransformer(RasterElementTransformer[TypeVarParameter]):

    @override
    def modify_parameter(self, parameter: TypeVarParameter, value: float64) -> None:
        # ToDo: parameterstep
        if not numpy.isnan(value):
            parameter(value)


class RasterSubunitIdentityTransformer(RasterSubunitTransformer[TypeVarParameter]):

    @override
    def modify_parameter(
        self, parameter: TypeVarParameter, values: dict[int64, float64]
    ) -> None:
        # ToDo: parameterstep
        for idx, value in values.items():
            if not numpy.isnan(value):
                parameter.values[idx] = value
