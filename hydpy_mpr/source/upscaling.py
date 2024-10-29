from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from numpy import float64, int64, nan

from hydpy_mpr.source.regionalisation import RasterEquation


@dataclass
class RasterUpscaler(ABC):

    equation: RasterEquation
    id2value: dict[int64, float64] = field(init=False)

    def __post_init__(self) -> None:
        self.id2value = {id_: float64(nan) for id_ in self.equation.group.id2element}

    @property
    def name2value(self) -> dict[str, float64]:
        id2element = self.equation.group.id2element
        return {id2element[id_]: value for id_, value in self.id2value.items()}

    @abstractmethod
    def scale_up(self) -> None:
        pass
