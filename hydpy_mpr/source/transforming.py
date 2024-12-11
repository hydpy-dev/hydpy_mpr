from __future__ import annotations
import abc
import dataclasses

import hydpy
import numpy

from hydpy_mpr.source import upscaling
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Transformer(Generic[TypeVarUpscaler, TypeVarParameter], abc.ABC):

    parameter: type[TypeVarParameter]
    model: str | None = dataclasses.field(default_factory=lambda: None)
    selection: hydpy.Selection | None = dataclasses.field(default_factory=lambda: None)
    hp: hydpy.HydPy = dataclasses.field(init=False)
    upscaler: TypeVarUpscaler = dataclasses.field(init=False)
    element2parameter: dict[str, TypeVarParameter] = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, upscaler: TypeVarUpscaler) -> None:
        self.hp = hp
        self.upscaler = upscaler
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
class ElementTransformer(
    Transformer[upscaling.ElementUpscaler[Any, Any], TypeVarParameter], abc.ABC
):

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
class SubunitTransformer(
    Transformer[upscaling.SubunitUpscaler[Any, Any], TypeVarParameter], abc.ABC
):

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


class ElementIdentityTransformer(ElementTransformer[TypeVarParameter]):

    @override
    def modify_parameter(self, parameter: TypeVarParameter, value: float64) -> None:
        # ToDo: parameterstep
        if not numpy.isnan(value):
            parameter(value)


class SubunitIdentityTransformer(SubunitTransformer[TypeVarParameter]):

    @override
    def modify_parameter(
        self, parameter: TypeVarParameter, values: dict[int64, float64]
    ) -> None:
        # ToDo: parameterstep
        for idx, value in values.items():
            if not numpy.isnan(value):
                parameter.values[idx] = value
