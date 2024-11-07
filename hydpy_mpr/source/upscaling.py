from __future__ import annotations
import abc
import dataclasses

import numpy

from hydpy_mpr.source import configuration
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass
class RasterUpscaler(abc.ABC):

    config: configuration.Config = dataclasses.field(init=False)
    task: configuration.RasterTask[Any] = dataclasses.field(init=False)
    id2value: dict[int64, float64] = dataclasses.field(init=False)

    def activate(
        self, config: configuration.Config, /, *, task: configuration.RasterTask[Any]
    ) -> None:
        self.config = config
        self.task = task
        self.id2value = {
            id_: float64(numpy.nan) for id_ in self.task.equation.group.id2element
        }

    @property
    def name2value(self) -> dict[str, float64]:
        id2element = self.task.equation.group.id2element
        return {id2element[id_]: value for id_, value in self.id2value.items()}

    @abc.abstractmethod
    def scale_up(self) -> None:
        pass
