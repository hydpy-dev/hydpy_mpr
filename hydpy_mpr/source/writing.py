from __future__ import annotations
import dataclasses

from hydpy import pub

from hydpy_mpr.source import configuration


@dataclasses.dataclass
class Writer:

    controldir: str = dataclasses.field(default="default")

    config: configuration.Config = dataclasses.field(init=False)

    def activate(self, config: configuration.Config) -> None:
        self.config = config

    def write(self) -> None:
        config = self.config
        calib = config.calibrator
        calib.perform_calibrationstep(calib.values)
        pub.controlmanager.currentdir = self.controldir
        config.hp.save_controls()