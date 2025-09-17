from __future__ import annotations
import abc
import dataclasses
import os

import hydpy
from hydpy import pub

from hydpy_mpr.source import calibrating
from hydpy_mpr.source.typing_ import *


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
