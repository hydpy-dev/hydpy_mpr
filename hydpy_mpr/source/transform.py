from __future__ import annotations
import abc

import hydpy

from hydpy_mpr.source import upscaling
from hydpy_mpr.source.typing_ import *


class RasterTransformer(Generic[TP]):

    selection: hydpy.Selection
    upscaler: upscaling.RasterUpscaler
    model2parameter: dict[str, type[TP]]
    element2parameter: dict[str, TP]

    def __init__(self, **model2parameter: type[TP]) -> None:
        self.model2parameter = model2parameter

    def activate(
        self, *, selection: hydpy.Selection, upscaler: upscaling.RasterUpscaler
    ) -> None:
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

    @abc.abstractmethod
    def modify_parameter(self, parameter: TP, value: float64) -> None:
        pass
