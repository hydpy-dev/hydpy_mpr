import os


from hydpy_mpr import testing


from hydpy_mpr.source.reading import RasterFloat, RasterGroup
from hydpy_mpr.source.regionalisation import Coefficient, RasterEquation
from hydpy_mpr.source.transform import RasterTransformer, TP
from hydpy_mpr.source.upscaling import RasterUpscaler


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
    "Coefficient",
    "RasterEquation",
    "RasterFloat",
    "RasterGroup",
    "RasterTransformer",
    "RasterUpscaler",
    "TP",
]
