from __future__ import annotations
import abc

import hydpy

from hydpy_mpr.source import managing
from hydpy_mpr.source.typing_ import *


class RasterTransformer(Generic[TP]):

    selection: hydpy.Selection | None
    model2parameter: dict[str, type[TP]]
    element2parameter: dict[str, TP]
    task: managing.RasterTask[TP]
    mpr: managing.MPR

    def __init__(
        self, *, selection: hydpy.Selection | None = None, **model2parameter: type[TP]
    ) -> None:
        self.selection = selection
        self.model2parameter = model2parameter

    def activate(self, mpr: managing.MPR, /, *, task: managing.RasterTask[TP]) -> None:
        self.mpr = mpr
        self.task = task
        if self.selection is None:
            elements = self.mpr.hp.elements
        else:
            elements = self.selection.elements
        element2parameter = {}
        for model, parametertype in self.model2parameter.items():
            for element in elements:
                if model == element.model.name:
                    parameter = element.model.parameters.control[parametertype.name]
                    assert isinstance(parameter, parametertype)
                    element2parameter[element.name] = parameter
        self.element2parameter = element2parameter

    def modify_parameters(self) -> None:
        element2parameter = self.element2parameter
        for name, value in self.task.upscaler.name2value.items():
            if (parameter := element2parameter.get(name)) is not None:
                self.modify_parameter(parameter=parameter, value=value)

    @abc.abstractmethod
    def modify_parameter(self, parameter: TP, value: float64) -> None:
        pass
