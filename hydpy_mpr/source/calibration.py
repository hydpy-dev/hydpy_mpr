from __future__ import annotations
import abc

from hydpy.core import typingtools
import nlopt
import numpy

from hydpy_mpr.source import configuration
from hydpy_mpr.source.typing_ import *


class Calibrator(abc.ABC):

    conditions: typingtools.Conditions
    config: configuration.Config
    values: tuple[float, ...]
    likelihood: float

    def activate(self, config: configuration.Config, /) -> None:
        self.config = config
        self.conditions = config.hp.conditions
        self.values = tuple(config.values)
        self.likelihood = numpy.nan

    @abc.abstractmethod
    def calculate_likelihood(self) -> float: ...

    def perform_calibrationstep(
        self,  # pylint: disable=unused-argument
        values: Sequence[float],
        *args: Any,
        **kwargs: Any,
    ) -> float:
        for coefficient, value in zip(self.config.coefficients, values):
            coefficient.value = value
        for task in self.config.tasks:
            task.run()
        self.config.hp.conditions = self.conditions
        self.config.hp.simulate()
        likelihood = self.calculate_likelihood()
        return likelihood

    def calibrate(self, *, maxeval: int | None = None) -> None:
        config = self.config
        optimiser = nlopt.opt(nlopt.LN_BOBYQA, len(config.coefficients))
        if maxeval is not None:
            optimiser.set_maxeval(maxeval=maxeval)
        optimiser.set_lower_bounds(config.lowers)
        optimiser.set_upper_bounds(config.uppers)
        optimiser.set_max_objective(self.perform_calibrationstep)
        self.values = tuple(optimiser.optimize(self.values))
        self.likelihood = self.perform_calibrationstep(self.values)
