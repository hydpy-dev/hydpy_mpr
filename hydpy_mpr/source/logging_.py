from __future__ import annotations
import abc
import dataclasses
import operator
import os
import warnings

import hydpy
import math
import numpy

from hydpy_mpr.source import calibrating
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True, repr=False)
class Logger(abc.ABC):

    hp: hydpy.HydPy = dataclasses.field(init=False)
    calibrator: calibrating.Calibrator = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, calibrator: calibrating.Calibrator) -> None:
        self.hp = hp
        self.calibrator = calibrator

    @abc.abstractmethod
    def log(self, likelihood: float) -> None:
        pass


@dataclasses.dataclass(kw_only=True, repr=False)
class DefaultLogger(Logger):

    filepath: str
    documentation: Sequence[str] | str | None = None
    overwrite: bool = False

    @override
    def activate(self, *, hp: hydpy.HydPy, calibrator: calibrating.Calibrator) -> None:

        super().activate(hp=hp, calibrator=calibrator)

        os.makedirs(os.path.split(self.filepath)[0], exist_ok=True)
        if os.path.exists(self.filepath):
            if self.overwrite:
                os.remove(self.filepath)
            else:
                raise PermissionError(
                    f"Overwriting the already existing log file `{self.filepath}` is "
                    f"not allowed."
                )

    @override
    def log(self, likelihood: float) -> None:

        with open(self.filepath, "a", encoding="utf-8") as logfile:

            if self.calibrator.nmb_steps == 1:
                if (documentation := self.documentation) is not None:
                    if not isinstance(documentation, str):
                        documentation = "\n".join(documentation)
                    logfile.write(documentation)
                    logfile.write("\n\n")
                header = ["likelihood"] + [c.name for c in self.calibrator.coefficients]
                logfile.write("\t".join(header))
                logfile.write("\n")

            values = [str(likelihood)]
            values.extend(str(c.value) for c in self.calibrator.coefficients)
            logfile.write("\t".join(values))
            logfile.write("\n")

    def reload(self, maximisation: bool) -> float:

        with open(self.filepath, "r", encoding="utf-8") as logfile:
            lines = logfile.readlines()

        if maximisation:
            comparer, best_value = operator.gt, -numpy.inf
        else:
            comparer, best_value = operator.lt, numpy.inf
        best_line: str | None = None

        saw_header = False
        for line in lines:
            line = line.strip()
            if line:
                first_entry = line.split(maxsplit=1)[0]
                if saw_header:
                    value = float(first_entry)
                    if comparer(value, best_value):
                        best_value, best_line = value, line
                elif first_entry == "likelihood":
                    saw_header = True

        if best_line is None:
            raise RuntimeError(f"The log file `{self.filepath}` is empty or corrupted.")

        values = [float(v) for v in best_line.split()[1:]]
        best_value_again = self.calibrator.perform_calibrationstep(
            values, apply_loggers=False
        )

        if not math.isclose(best_value, best_value_again):
            warnings.warn(
                f"The best likelihood value taken from the log file `{self.filepath}` "
                f"is `{best_value}, but re-applying the corresponding coefficients "
                f"results in `{best_value_again}`."
            )

        return best_value_again
