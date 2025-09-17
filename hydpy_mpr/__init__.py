from __future__ import annotations
import os


from hydpy_mpr import testing


from hydpy_mpr.source.calibrating import Calibrator, GridCalibrator, NLOptCalibrator
from hydpy_mpr.source.logging_ import DefaultLogger, Logger
from hydpy_mpr.source.managing import MPR, RasterElementTask, RasterSubunitTask
from hydpy_mpr.source.preprocessing import RasterPreprocessor
from hydpy_mpr.source.reading import (
    AttributeFloat,
    AttributeInt,
    FeatureClass,
    FeatureClasses,
    RasterFloat,
    RasterGroup,
    RasterGroups,
    RasterInt,
    read_geotiff,
    read_mapping_table,
)
from hydpy_mpr.source.regionalising import (
    Coefficient,
    AttributeRegionaliser,
    AttributeSubregionaliser,
    RasterRegionaliser,
    RasterSubregionaliser,
)
from hydpy_mpr.source.transforming import (
    ElementIdentityTransformer,
    ElementTransformer,
    SubunitIdentityTransformer,
    SubunitTransformer,
    TypeVarParameter,
)
from hydpy_mpr.source.upscaling import (
    AttributeElementDefaultUpscaler,
    AttributeElementUpscaler,
    AttributeSubunitDefaultUpscaler,
    AttributeSubunitUpscaler,
    AttributeUpscaler,
    ElementUpscaler,
    RasterElementDefaultUpscaler,
    RasterElementUpscaler,
    RasterSubunitDefaultUpscaler,
    RasterSubunitUpscaler,
    RasterUpscaler,
    SubunitUpscaler,
    Upscaler,
)
from hydpy_mpr.source.writing import ControlWriter, ParameterTableWriter, Writer


__version__ = "0.0.dev0"


if os.path.exists(os.path.join(testing.__path__[0], ".hydpy_mpr_doctest_hack")):
    # Support the POSIX path separator also when executing doctests on Windows:

    from doctest import OutputChecker

    _original = OutputChecker._toAscii  # type: ignore[attr-defined]  # pylint: disable=protected-access

    def _modified(self: OutputChecker, s: str) -> str:
        s = _original(self, s)
        return s.replace("\\", "/")

    OutputChecker._toAscii = _modified  # type: ignore[attr-defined]  # pylint: disable=protected-access


__all__ = [
    "AttributeElementDefaultUpscaler",
    "AttributeElementUpscaler",
    "AttributeFloat",
    "AttributeInt",
    "AttributeRegionaliser",
    "AttributeSubregionaliser",
    "AttributeSubunitDefaultUpscaler",
    "AttributeSubunitUpscaler",
    "AttributeUpscaler",
    "Calibrator",
    "Coefficient",
    "ControlWriter",
    "DefaultLogger",
    "ElementIdentityTransformer",
    "ElementTransformer",
    "ElementUpscaler",
    "FeatureClass",
    "FeatureClasses",
    "GridCalibrator",
    "Logger",
    "MPR",
    "NLOptCalibrator",
    "ParameterTableWriter",
    "RasterElementDefaultUpscaler",
    "RasterElementUpscaler",
    "RasterElementTask",
    "RasterFloat",
    "RasterGroup",
    "RasterGroups",
    "RasterInt",
    "RasterPreprocessor",
    "RasterRegionaliser",
    "RasterSubregionaliser",
    "RasterSubunitDefaultUpscaler",
    "RasterSubunitTask",
    "RasterSubunitUpscaler",
    "RasterUpscaler",
    "SubunitIdentityTransformer",
    "SubunitTransformer",
    "SubunitUpscaler",
    "read_geotiff",
    "read_mapping_table",
    "TypeVarParameter",
    "Upscaler",
    "Writer",
]
