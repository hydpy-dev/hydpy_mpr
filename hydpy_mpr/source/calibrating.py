from __future__ import annotations
import abc
import dataclasses

import hydpy
from hydpy.core import typingtools
import nlopt
import numpy

from hydpy_mpr.source import regionalising
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Calibrator(abc.ABC):
    conditions: typingtools.Conditions = dataclasses.field(init=False)
    hp: hydpy.HydPy = dataclasses.field(init=False)
    tasks: Tasks = dataclasses.field(init=False)
    likelihood: float = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, tasks: Tasks) -> None:
        self.hp = hp
        self.tasks = tasks
        self.conditions = hp.conditions
        self.likelihood = numpy.nan

    @property
    def coefficients(self) -> tuple[regionalising.Coefficient, ...]:
        coefficients: set[regionalising.Coefficient] = set()
        for task in self.tasks:
            coefficients.update(task.regionaliser.coefficients)
        return tuple(sorted(coefficients, key=lambda c: c.name))

    @property
    def lowers(self) -> tuple[float, ...]:
        return tuple(c.lower for c in self.coefficients)

    @property
    def uppers(self) -> tuple[float, ...]:
        return tuple(c.upper for c in self.coefficients)

    @property
    def values(self) -> tuple[float, ...]:
        return tuple(c.value for c in self.coefficients)

    @abc.abstractmethod
    def calculate_likelihood(self) -> float: ...

    def perform_calibrationstep(
        self,  # pylint: disable=unused-argument
        values: Sequence[float],
        *args: Any,
        **kwargs: Any,
    ) -> float:
        for coefficient, value in zip(self.coefficients, values):
            coefficient.value = value
        for task in self.tasks:
            task.run()
        self.hp.conditions = self.conditions
        self.hp.simulate()
        likelihood = self.calculate_likelihood()
        return likelihood

    @abc.abstractmethod
    def calibrate(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class NLOptCalibrator(Calibrator, abc.ABC):

    algorithm: int = dataclasses.field(default_factory=lambda: nlopt.LN_BOBYQA)
    maxeval: int | None = dataclasses.field(default_factory=lambda: None)

    @override
    def calibrate(self) -> None:
        optimiser = nlopt.opt(self.algorithm, len(self.coefficients))
        if (maxeval := self.maxeval) is not None:
            optimiser.set_maxeval(maxeval=maxeval)
        optimiser.set_lower_bounds(self.lowers)
        optimiser.set_upper_bounds(self.uppers)
        optimiser.set_max_objective(self.perform_calibrationstep)
        values = optimiser.optimize(self.values)
        for coefficient, value in zip(self.coefficients, values):
            coefficient.value = value
        self.likelihood = self.perform_calibrationstep(self.values)
