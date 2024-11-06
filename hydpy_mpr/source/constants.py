"""This module contains all constants defined by HydPy-MPR."""

from __future__ import annotations


# Default no data value for float raster data:
NODATA_FLOAT = -9999.0

# Default no data value for integer raster data:
NODATA_INT = -9999

# Name of the GeoPackage database:
FEATURE_GPKG = "feature.gpkg"

# Table for mapping element IDs to element names required when working with raster
# files:
MAPPING_TABLE = "element_id2name"

# Name of the mapping table's element ID column and the corresponding raster file:
ELEMENT_ID = "element_id"

# Name of the mapping table's element name column:
ELEMENT_NAME = "element_name"
