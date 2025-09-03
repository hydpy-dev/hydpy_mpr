from hydpy_mpr.source.typing_ import *

def arithmetic_mean_for_raster_element(
    *,
    element_id: MatrixInt,
    mask: MatrixBool,
    output: MatrixFloat,
    id2value: dict[int64, float64],
) -> None: ...
def arithmetic_mean_for_raster_subunit(
    *,
    element_id: MatrixInt,
    subunit_id: MatrixInt,
    mask: MatrixBool,
    output: MatrixFloat,
    id2idx2value: dict[int64, dict[int64, float64]],
) -> None: ...
