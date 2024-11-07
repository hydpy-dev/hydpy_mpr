from __future__ import annotations
import abc

import hydpy
from hydpy.core import typingtools
import nlopt
import numpy

from hydpy_mpr.source import configuration
from hydpy_mpr.source.typing_ import *


class Calibrator(abc.ABC):

    hp: hydpy.HydPy
    conditions: typingtools.Conditions
    config: configuration.Config

    def activate(self, hp: hydpy.HydPy, config: configuration.Config) -> None:
        self.hp = hp
        self.conditions = hp.conditions
        self.config = config

    @abc.abstractmethod
    def calculate_likelihood(self) -> float: ...

    def perform_calibrationstep(
        self, values: Sequence[float], *args: Any, **kwargs: Any
    ) -> float:
        for coefficient, value in zip(self.config.coefficients, values):
            coefficient.value = value
        for task in self.config.tasks:
            task.run()
        self.hp.conditions = self.conditions
        self.hp.simulate()
        likelihood = self.calculate_likelihood()
        return likelihood

    def calibrate(self, *, maxeval: int | None = None) -> tuple[float, VectorFloat]:
        config = self.config
        optimiser = nlopt.opt(nlopt.LN_BOBYQA, len(config.coefficients))
        if maxeval is not None:
            optimiser.set_maxeval(maxeval=maxeval)
        optimiser.set_lower_bounds(config.lowers)
        optimiser.set_upper_bounds(config.uppers)
        optimiser.set_max_objective(self.perform_calibrationstep)
        opt_values = optimiser.optimize(config.values)
        likelihood = self.perform_calibrationstep(opt_values)
        assert isinstance(opt_values, numpy.ndarray)
        return likelihood, opt_values
