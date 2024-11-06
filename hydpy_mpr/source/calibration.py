from __future__ import annotations
from abc import ABC, abstractmethod

from hydpy import HydPy, nse
from hydpy.core.typingtools import Conditions
from nlopt import opt, LN_BOBYQA
from numpy import ndarray

from hydpy_mpr.source.configuration import Config
from hydpy_mpr.source.typing_ import Any, Sequence, VectorFloat


class Calibrator(ABC):

    hp: HydPy
    conditions: Conditions
    config: Config

    def activate(self, hp: HydPy, config: Config) -> None:
        self.hp = hp
        self.conditions = hp.conditions
        self.config = config

    @abstractmethod
    def calculate_likelihood(self) -> float:
        ...

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

    def run(self, *, maxeval: int | None = None) -> tuple[float, VectorFloat]:
        config = self.config
        o = opt(LN_BOBYQA, len(config.coefficients))
        if maxeval is not None:
            o.set_maxeval(maxeval=maxeval)
        o.set_lower_bounds(config.lowers)
        o.set_upper_bounds(config.uppers)
        o.set_max_objective(self.perform_calibrationstep)
        opt_values = o.optimize(config.values)
        likelihood = self.perform_calibrationstep(opt_values)
        assert isinstance(opt_values, ndarray)
        return likelihood, opt_values
