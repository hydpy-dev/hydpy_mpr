from __future__ import annotations
import abc
import dataclasses
import os

import hydpy
from hydpy import pub
from hydpy.auxs.statstools import Criterion, SummaryRow

from hydpy_mpr.source import calibrating
from hydpy_mpr.source.typing_ import *


StepSize: TypeAlias = Literal["daily", "d", "monthly", "m"]
Aggregator: TypeAlias = str | Callable[[Sequence[float] | VectorFloat], float]


@dataclasses.dataclass(kw_only=True, repr=False)
class Writer(abc.ABC):

    hp: hydpy.HydPy = dataclasses.field(init=False)
    calibrator: calibrating.Calibrator = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, calibrator: calibrating.Calibrator) -> None:
        self.hp = hp
        self.calibrator = calibrator

    @abc.abstractmethod
    def write(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True, repr=False)
class ControlWriter(Writer):

    controldir: str = dataclasses.field(default="default")

    @override
    def write(self) -> None:
        pub.controlmanager.currentdir = self.controldir
        self.hp.save_controls()


@dataclasses.dataclass(kw_only=True, repr=False)
class ParameterTableWriter(Writer):

    filepath: str
    overwrite: bool = False
    header_parameter: str = "parameter"
    header_lower: str = "lower"
    header_upper: str = "upper"
    header_value: str = "value"

    @override
    def write(self) -> None:

        os.makedirs(os.path.split(self.filepath)[0], exist_ok=True)
        if os.path.exists(self.filepath) and not self.overwrite:
            raise PermissionError(
                f"Overwriting the already existing parameter result file "
                f"`{self.filepath} is not allowed."
            )

        with open(self.filepath, "w", encoding="utf-8") as parfile:
            header = [
                self.header_parameter,
                self.header_lower,
                self.header_upper,
                self.header_value,
            ]
            parfile.write("\t".join(header))
            parfile.write("\n")
            for c in self.calibrator.coefficients:
                values = [str(v) for v in (c.name, c.lower, c.upper, c.value)]
                parfile.write("\t".join(values))
                parfile.write("\n")


@dataclasses.dataclass(kw_only=True, repr=False)
class EfficiencyTableWriter(Writer):

    filepath: str
    overwrite: bool = False
    nodes: Sequence[hydpy.Node]
    criteria: Sequence[Criterion]
    nodenames: Sequence[str] | None = None
    critnames: Sequence[str] | None = None
    critfactors: Sequence[float] | float = 1.0
    critdigits: Sequence[int] | int = 2
    subperiod: bool = True
    average: bool = True
    averagename: str = "mean"
    summaryrows: Sequence[SummaryRow] = dataclasses.field(default_factory=lambda: ())
    filter_: float = 0.0
    stepsize_and_aggregator: tuple[StepSize, Aggregator] | None = None
    missingvalue: str = "-"
    decimalseperator: str = "."

    @override
    def write(self) -> None:

        os.makedirs(os.path.split(self.filepath)[0], exist_ok=True)
        if os.path.exists(self.filepath) and not self.overwrite:
            raise PermissionError(
                f"Overwriting the already existing efficiency result file "
                f"`{self.filepath} is not allowed."
            )

        with open(self.filepath, "w", encoding="utf-8") as efffile:
            if self.stepsize_and_aggregator is None:
                hydpy.print_evaluationtable(
                    nodes=self.nodes,
                    criteria=self.criteria,
                    nodenames=self.nodenames,
                    critnames=self.critnames,
                    critfactors=self.critfactors,
                    critdigits=self.critdigits,
                    subperiod=self.subperiod,
                    average=self.average,
                    averagename=self.averagename,
                    summaryrows=self.summaryrows,
                    filter_=self.filter_,
                    missingvalue=self.missingvalue,
                    decimalseperator=self.decimalseperator,
                    file_=self.filepath,
                )
            else:
                hydpy.print_evaluationtable(
                    nodes=self.nodes,
                    criteria=self.criteria,
                    nodenames=self.nodenames,
                    critnames=self.critnames,
                    critfactors=self.critfactors,
                    critdigits=self.critdigits,
                    subperiod=self.subperiod,
                    average=self.average,
                    averagename=self.averagename,
                    summaryrows=self.summaryrows,
                    filter_=self.filter_,
                    stepsize=self.stepsize_and_aggregator[0],
                    aggregator=self.stepsize_and_aggregator[1],
                    missingvalue=self.missingvalue,
                    decimalseperator=self.decimalseperator,
                    file_=self.filepath,
                )


@dataclasses.dataclass(kw_only=True, repr=False)
class AggregatedEfficiencyTableWriter(Writer):

    filepath: str
    overwrite: bool = False
    nodes: Sequence[hydpy.Node]
    criteria: Sequence[Criterion]
    nodenames: Sequence[str] | None = None
    critnames: Sequence[str] | None = None
    critfactors: Sequence[float] | float = 1.0
    critdigits: Sequence[int] | int = 2
    subperiod: bool = True
    average: bool = True
    averagename: str = "mean"
    summaryrows: Sequence[SummaryRow] = dataclasses.field(default_factory=lambda: ())
    filter_: float = 0.0
    stepsize: Literal["daily", "d", "monthly", "m"] | None = None
    aggregator: str | Callable[[Sequence[float] | VectorFloat], float] = "mean"
    missingvalue: str = "-"
    decimalseperator: str = "."
