import hydpy
import hydpy_mpr as mpr


class MyCalibrator(mpr.Calibrator):

    def calculate_likelihood(self) -> float:
        return sum(hydpy.nse(node=node) for node in self.config.hp.nodes) / 4.0
