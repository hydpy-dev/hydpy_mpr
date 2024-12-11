from __future__ import annotations
import abc
import dataclasses

from hydpy_mpr.source import equations
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


class Preprocessor(
    equations.Equation[
        TypeVarProvider, TypeVarDataFloat, TypeVarArrayBool, TypeVarArrayFloat
    ],
    abc.ABC,
):

    @override
    def activate(self, *, provider: TypeVarProvider) -> None:
        super().activate(provider=provider)
        self.preprocess_data()
        self.provider.data[self.name] = self.TYPE_DATA_FLOAT(values=self.output)

    @abc.abstractmethod
    def preprocess_data(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class AttributePreprocessor(
    Preprocessor[reading.FeatureClass, reading.AttributeFloat, VectorBool, VectorFloat],
    equations.AttributeEquation,
    abc.ABC,
):
    pass


@dataclasses.dataclass(kw_only=True)
class RasterPreprocessor(
    Preprocessor[reading.RasterGroup, reading.RasterFloat, MatrixBool, MatrixFloat],
    equations.RasterEquation,
    abc.ABC,
):
    pass
