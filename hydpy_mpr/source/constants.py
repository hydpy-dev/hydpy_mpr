"""This module contains all constants defined by HydPy-MPR."""

from __future__ import annotations

from hydpy_mpr.source.typing_ import *


# Name of the raster directory:
RASTER = "raster"

# Name of the GeoPackage database:
FEATURE_GPKG = "feature.gpkg"

# Table for mapping element IDs to element names required when working with raster
# files:
MAPPING_TABLE = "element_id2name"

# Name of the mapping table's element ID column and the corresponding raster file:
ELEMENT_ID = "element_id"

# Name of the mapping table's element name column:
ELEMENT_NAME = "element_name"

# Name of the subunit ID raster file:
SUBUNIT_ID = "subunit_id"

# Names of the default upscaling methods (note: synchronise with `typing_`):
UP_A: Literal["arithmetic_mean"] = "arithmetic_mean"
UP_G: Literal["geometric_mean"] = "geometric_mean"
UP_H: Literal["harmonic_mean"] = "harmonic_mean"
