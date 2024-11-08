from __future__ import annotations
import abc
import dataclasses

from hydpy.core import typingtools
import nlopt
import numpy

from hydpy_mpr.source import managing
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass
class Calibrator(abc.ABC):

    conditions: typingtools.Conditions = dataclasses.field(init=False)
    mpr: managing.MPR = dataclasses.field(init=False)
    values: tuple[float, ...] = dataclasses.field(init=False)
    likelihood: float = dataclasses.field(init=False)

    def activate(self, mpr: managing.MPR, /) -> None:
        self.mpr = mpr
        self.conditions = mpr.hp.conditions
        self.values = tuple(mpr.values)
        self.likelihood = numpy.nan

    @abc.abstractmethod
    def calculate_likelihood(self) -> float: ...

    def perform_calibrationstep(
        self,  # pylint: disable=unused-argument
        values: Sequence[float],
        *args: Any,
        **kwargs: Any,
    ) -> float:
        for coefficient, value in zip(self.mpr.coefficients, values):
            coefficient.value = value
        for task in self.mpr.tasks:
            task.run()
        self.mpr.hp.conditions = self.conditions
        self.mpr.hp.simulate()
        likelihood = self.calculate_likelihood()
        return likelihood

    @abc.abstractmethod
    def calibrate(self) -> None:
        pass


@dataclasses.dataclass
class NLOptCalibrator(Calibrator, abc.ABC):

    algorithm: int = dataclasses.field(default_factory=lambda: nlopt.LN_BOBYQA)
    maxeval: int | None = dataclasses.field(default_factory=lambda: None)

    def calibrate(self) -> None:
        mpr = self.mpr
        optimiser = nlopt.opt(self.algorithm, len(mpr.coefficients))
        if (maxeval := self.maxeval) is not None:
            optimiser.set_maxeval(maxeval=maxeval)
        optimiser.set_lower_bounds(mpr.lowers)
        optimiser.set_upper_bounds(mpr.uppers)
        optimiser.set_max_objective(self.perform_calibrationstep)
        self.values = tuple(optimiser.optimize(self.values))
        self.likelihood = self.perform_calibrationstep(self.values)
