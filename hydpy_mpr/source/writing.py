from __future__ import annotations
import abc
import dataclasses

import hydpy
from hydpy import pub

from hydpy_mpr.source import calibrating
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass(kw_only=True)
class Writer(abc.ABC):

    controldir: str = dataclasses.field(default="default")
    hp: hydpy.HydPy = dataclasses.field(init=False)
    calibrator: calibrating.Calibrator = dataclasses.field(init=False)

    def activate(self, *, hp: hydpy.HydPy, calibrator: calibrating.Calibrator) -> None:
        self.hp = hp
        self.calibrator = calibrator

    @abc.abstractmethod
    def write(self) -> None:
        pass


@dataclasses.dataclass(kw_only=True)
class ControlWriter(Writer):

    @override
    def write(self) -> None:
        self.calibrator.perform_calibrationstep(self.calibrator.values)
        pub.controlmanager.currentdir = self.controldir
        self.hp.save_controls()
