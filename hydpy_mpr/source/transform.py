from __future__ import annotations
from abc import ABC, abstractmethod
from typing import overload

from hydpy import Selection
from hydpy.core.parametertools import Parameter
from numpy import float64

from hydpy_mpr.source.upscaling import RasterUpscaler
from hydpy_mpr.source.typing_ import Generic, Iterable, TypeVar

TP = TypeVar("TP", bound=Parameter)


class RasterTransformer(Generic[TP]):

    selection: Selection
    upscaler: RasterUpscaler
    model2parameter: dict[str, type[TP]]
    element2parameter: dict[str, TP]

    def __init__(self, **model2parameter: type[TP]) -> None:
        self.model2parameter = model2parameter

    def activate(self, *, selection: Selection, upscaler: RasterUpscaler) -> None:
        self.selection = selection
        self.upscaler = upscaler
        element2parameter = {}
        for model, parametertype in self.model2parameter.items():
            elements = self.selection.search_modeltypes(model).elements
            for element in elements:
                parameter = element.model.parameters.control[parametertype.name]
                assert isinstance(parameter, parametertype)
                element2parameter[element.name] = parameter
        self.element2parameter = element2parameter

    def modify_parameters(self) -> None:
        element2parameter = self.element2parameter
        for name, value in self.upscaler.name2value.items():
            if (parameter := element2parameter.get(name)) is not None:
                self.modify_parameter(parameter=parameter, value=value)

    @abstractmethod
    def modify_parameter(self, parameter: TP, value: float64) -> None:
        pass
