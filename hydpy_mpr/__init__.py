import os


from hydpy_mpr import testing


from hydpy_mpr.source.calibrating import Calibrator, NLOptCalibrator
from hydpy_mpr.source.managing import MPR, RasterElementTask, RasterSubunitTask
from hydpy_mpr.source.preprocessing import RasterPreprocessor
from hydpy_mpr.source.reading import RasterFloat, RasterGroup, RasterInt
from hydpy_mpr.source.regionalising import Coefficient, RasterRegionaliser
from hydpy_mpr.source.transforming import (
    RasterElementIdentityTransformer,
    RasterElementTransformer,
    RasterSubunitIdentityTransformer,
    RasterSubunitTransformer,
    TP,
)
from hydpy_mpr.source.upscaling import (
    RasterElementDefaultUpscaler,
    RasterElementUpscaler,
    RasterSubunitDefaultUpscaler,
    RasterSubunitUpscaler,
)
from hydpy_mpr.source.writing import ControlWriter, Writer


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
    "Calibrator",
    "Coefficient",
    "MPR",
    "ControlWriter",
    "NLOptCalibrator",
    "RasterElementDefaultUpscaler",
    "RasterElementIdentityTransformer",
    "RasterElementUpscaler",
    "RasterElementTask",
    "RasterElementTransformer",
    "RasterFloat",
    "RasterGroup",
    "RasterInt",
    "RasterPreprocessor",
    "RasterRegionaliser",
    "RasterSubunitDefaultUpscaler",
    "RasterSubunitIdentityTransformer",
    "RasterSubunitTask",
    "RasterSubunitTransformer",
    "RasterSubunitUpscaler",
    "TP",
    "Writer",
]
