from __future__ import annotations
import dataclasses

from hydpy_mpr.source import configuration


@dataclasses.dataclass
class Runner:

    config: configuration.Config = dataclasses.field(init=False)

    def activate(self, config: configuration.Config) -> None:
        self.config = config

    def run(self, maxeval: int) -> None:
        self.config.calibrator.calibrate(maxeval=maxeval)
        for writer in self.config.writers:
            writer.write()
