
from hydpy import nse

from hydpy_mpr import Calibrator


class MyCalibrator(Calibrator):

    def calculate_likelihood(self) -> float:
        return sum(nse(node=node) for node in self.hp.nodes) / 4.0