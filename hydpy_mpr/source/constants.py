"""This module contains all constants defined by HydPy-MPR."""

from __future__ import annotations
import enum

from hydpy_mpr.source.typing_ import *


# Name of the raster directory:
RASTER = "raster"

# Name of the GeoPackage database:
FEATURE_GPKG = "feature.gpkg"

# Table for mapping element IDs to element names required when working with raster
# files:
MAPPING_TABLE = "element_id2name"

# Name of the mapping table's element ID column and the corresponding raster file, as
# well as the feature classes' element ID columns:
ELEMENT_ID = "element_id"

# Name of the mapping table's element name column:
ELEMENT_NAME = "element_name"

# Name of the subunit ID raster file and the feature classes' subunit ID columns:
SUBUNIT_ID = "subunit_id"


class Size(enum.StrEnum):
    """Names of the feature classes' size-related columns."""

    AREA = "Area"  # for polygon features
    LENGTH = "Length"  # for line features
    # ToDo: something like "weight" for point features?

    @override
    def __repr__(self) -> str:
        return self._name_  # pylint: disable=no-member


# Names of the default upscaling methods (note: synchronise with `typing_`):
UP_A: Literal["arithmetic_mean"] = "arithmetic_mean"
UP_G: Literal["geometric_mean"] = "geometric_mean"
UP_H: Literal["harmonic_mean"] = "harmonic_mean"
