from __future__ import annotations
import abc
import concurrent.futures
import dataclasses
import itertools

import hydpy
from hydpy.core import typingtools
import nlopt
import numpy

from hydpy_mpr.source import logging_
from hydpy_mpr.source import regionalising
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True, repr=False)
class Calibrator(abc.ABC):
    conditions: typingtools.Conditions = dataclasses.field(init=False)
    hp: hydpy.HydPy = dataclasses.field(init=False)
    tasks: Tasks = dataclasses.field(init=False)
    subregionalisers: Sequence[
        regionalising.AttributeSubregionaliser | regionalising.RasterSubregionaliser
    ] = dataclasses.field(init=False)
    loggers: Sequence[logging_.Logger] = dataclasses.field(init=False)
    likelihood: float = dataclasses.field(init=False)
    nmb_steps: int = dataclasses.field(init=False, default=0)

    def activate(
        self,
        *,
        hp: hydpy.HydPy,
        tasks: Tasks,
        subregionalisers: Sequence[
            regionalising.AttributeSubregionaliser | regionalising.RasterSubregionaliser
        ],
        loggers: Sequence[logging_.Logger],
    ) -> None:
        self.hp = hp
        self.tasks = tasks
        self.subregionalisers = subregionalisers
        self.loggers = loggers
        self.conditions = hp.conditions
        self.likelihood = numpy.nan

    @property
    def coefficients(self) -> Sequence[regionalising.Coefficient]:
        coefficients: set[regionalising.Coefficient] = set()
        for subregionaliser in self.subregionalisers:
            coefficients.update(subregionaliser.coefficients)
        for task in self.tasks:
            coefficients.update(task.regionaliser.coefficients)
        return tuple(sorted(coefficients, key=lambda c: c.name))

    @property
    def lowers(self) -> Sequence[float]:
        return tuple(c.lower for c in self.coefficients)

    @property
    def uppers(self) -> Sequence[float]:
        return tuple(c.upper for c in self.coefficients)

    @property
    def values(self) -> Sequence[float]:
        return tuple(c.value for c in self.coefficients)

    def update_coefficients(self, values: Sequence[float]) -> None:
        for coefficient, value in zip(self.coefficients, values):
            coefficient.value = value

    @abc.abstractmethod
    def calculate_likelihood(self) -> float: ...

    def perform_calibrationstep(
        self,  # pylint: disable=unused-argument
        values: Sequence[float],
        *args: Any,
        **kwargs: Any,
    ) -> float:
        self.update_coefficients(values)
        for subregionaliser in self.subregionalisers:
            subregionaliser.apply_coefficients()
        if (threads := hydpy.pub.options.threads) == 0:
            for task in self.tasks:
                task.run()
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = (executor.submit(task.run) for task in self.tasks)
                for future in concurrent.futures.as_completed(futures):
                    pass
        self.hp.update_parameters()
        self.hp.conditions = self.conditions
        self.hp.simulate()
        likelihood = self.calculate_likelihood()
        self.nmb_steps += 1
        for logger in self.loggers:
            logger.log(likelihood=likelihood)
        return likelihood

    @abc.abstractmethod
    def calibrate(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True, repr=False)
class GridCalibrator(Calibrator, abc.ABC):

    nmb_nodes: int

    def check_coefficients(self) -> None:

        def _raise_error(upper_or_lower: Literal["lower", "upper"]) -> NoReturn:
            raise ValueError(
                f"Class `{type(self).__name__}` requires lower and upper bounds for "
                f"all coefficients, but coefficient `{coef.name}` defines no "
                f"{upper_or_lower} bound."
            )

        for coef in self.coefficients:
            if numpy.isinf(coef.lower):
                _raise_error("lower")
            if numpy.isinf(coef.upper):
                _raise_error("upper")

    @property
    def gridpoints(self) -> Iterator[Sequence[float]]:
        self.check_coefficients()
        if self.nmb_nodes == 1:
            nodes = (0.5,)
        else:
            nodes = tuple(numpy.linspace(0.0, 1.0, self.nmb_nodes))
        coefs = self.coefficients
        for factors in itertools.product(nodes, repeat=len(coefs)):
            yield tuple(
                coef.lower + factor * (coef.upper - coef.lower)
                for coef, factor in zip(coefs, factors)
            )

    @override
    def calibrate(self) -> None:
        best_likelihood = -numpy.inf
        best_values: Sequence[float] = len(self.coefficients) * (numpy.nan,)
        for values in self.gridpoints:
            likelihood = self.perform_calibrationstep(values)
            if likelihood > best_likelihood:
                best_likelihood = likelihood
                best_values = values
        self.likelihood = self.perform_calibrationstep(best_values)


@dataclasses.dataclass(kw_only=True, repr=False)
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
        self.update_coefficients(values)
        self.likelihood = self.perform_calibrationstep(self.values)
