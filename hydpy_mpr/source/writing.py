from __future__ import annotations
import abc
import dataclasses

from hydpy import pub

from hydpy_mpr.source import managing
from hydpy_mpr.source.typing_ import *


@dataclasses.dataclass
class Writer(abc.ABC):

    controldir: str = dataclasses.field(default="default")

    mpr: managing.MPR = dataclasses.field(init=False)

    def activate(self, mpr: managing.MPR) -> None:
        self.mpr = mpr

    @abc.abstractmethod
    def write(self) -> None:
        pass


class ControlWriter(Writer):

    @override
    def write(self) -> None:
        mpr = self.mpr
        calib = mpr.calibrator
        calib.perform_calibrationstep(calib.values)
        pub.controlmanager.currentdir = self.controldir
        mpr.hp.save_controls()
