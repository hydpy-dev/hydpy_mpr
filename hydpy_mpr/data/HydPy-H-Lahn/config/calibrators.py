import hydpy
import hydpy_mpr


class MyCalibrator(hydpy_mpr.NLOptCalibrator):

    def calculate_likelihood(self) -> float:
        return sum(hydpy.nse(node=node) for node in self.hp.nodes) / 4.0
