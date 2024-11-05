from dataclasses import dataclass

from hydpy_mpr.source.regionalisation import RasterEquation
from hydpy_mpr.source.upscaling import RasterUpscaler
from hydpy_mpr.source.transform import RasterTransformer, TP
from hydpy_mpr.source.typing_ import Generic


@dataclass
class RasterTask(Generic[TP]):

    equation: RasterEquation
    upscaler: RasterUpscaler
    transformers: list[RasterTransformer[TP]]


@dataclass
class Config(Generic[TP]):

    tasks: list[RasterTask[TP]]
    subequations: list[RasterEquation]
