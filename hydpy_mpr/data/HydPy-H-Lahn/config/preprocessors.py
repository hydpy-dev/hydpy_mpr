import dataclasses

import hydpy_mpr


@dataclasses.dataclass
class DataSelector(hydpy_mpr.RasterPreprocessor):

    source_1m: str
    source_2m: str
    source_landuse: str

    dataset_1m: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    dataset_2m: hydpy_mpr.RasterFloat = dataclasses.field(init=False)
    dataset_landuse: hydpy_mpr.RasterInt = dataclasses.field(init=False)

    def preprocess_data(self) -> None:
        idxs_1m = self.dataset_landuse.values == 1
        self.output[idxs_1m] = self.dataset_1m.values[idxs_1m]
        idxs_2m = self.dataset_landuse.values == 2
        self.output[idxs_2m] = self.dataset_2m.values[idxs_2m]
        # self.mask = idxs_1m + idxs_2m  # ToDo


@dataclasses.dataclass
class SoilDepth(hydpy_mpr.RasterPreprocessor):

    source_landuse: str

    dataset_landuse: hydpy_mpr.RasterInt = dataclasses.field(init=False)

    def preprocess_data(self) -> None:
        idxs_1m = self.dataset_landuse.values == 1
        self.output[idxs_1m] = 1.0
        idxs_2m = self.dataset_landuse.values == 2
        self.output[idxs_2m] = 2.0
        # self.mask = idxs_1m + idxs_2m  # ToDo
