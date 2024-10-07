"""Utilities for reading the raster, feature, and table data."""

import os.path
import warnings

from fudgeo.geopkg import GeoPackage

from hydpy_mpr.source.constants import ELEMENT_ID, ELEMENT_NAME, MAPPING_TABLE
from hydpy_mpr.source.typing_ import MappingTable


def read_mapping_table(filepath: str, /) -> MappingTable:
    """Read the table for mapping element IDs to element names required when working
    with raster files.

    >>> from fudgeo.geopkg import Field, GeoPackage
    >>> from hydpy.core.testtools import warn_later
    >>> from hydpy_mpr.source.constants import ELEMENT_ID, ELEMENT_NAME, MAPPING_TABLE
    >>> from hydpy_mpr.source.readutils import read_mapping_table
    >>> from hydpy_mpr.testing import prepare_project

    >>> reset_workingdir = prepare_project("HydPy-H-Lahn")

    Everything okay:

    >>> read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    {1: 'land_dill_assl', 2: 'land_lahn_kalk', 3: 'land_lahn_leun', 4: 'land_lahn_marb'}

    Missing file:

    >>> read_mapping_table("HydPy-H-Lahn/mpr_data/veature.gpkg")
    Traceback (most recent call last):
    ...
    FileNotFoundError: Geopackage `HydPy-H-Lahn/mpr_data/veature.gpkg` does not exist.

    ID column missing:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> gpkg.tables[MAPPING_TABLE].drop()
    >>> gpkg.connection.close()
    >>> read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    Traceback (most recent call last):
    ...
    TypeError: Geopackage `HydPy-H-Lahn/mpr_data/feature.gpkg` does not contain the \
required mapping table `element_id2name`.

    Name column missing:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> _ = gpkg.create_table(MAPPING_TABLE, fields=())
    >>> gpkg.connection.close()
    >>> read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    Traceback (most recent call last):
    ...
    TypeError: Geopackage `HydPy-H-Lahn/mpr_data/feature.gpkg` does not contain a \
column named `element_id`.

    ID of wrong type:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> x = Field(name=ELEMENT_ID, data_type="DOUBLE")
    >>> y = Field(name=ELEMENT_NAME, data_type="INTEGER")
    >>> _ = gpkg.create_table(MAPPING_TABLE, fields=(x, y), overwrite=True)
    >>> with gpkg.connection as connection:
    ...     _ = connection.execute(
    ...         f"INSERT INTO {MAPPING_TABLE}"
    ...         f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES (1.5, 2)"
    ...     )
    >>> gpkg.connection.close()
    >>> read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    Traceback (most recent call last):
    ...
    TypeError: Column `element_id` of table `element_id2name` of geopackage \
`HydPy-H-Lahn/mpr_data/feature.gpkg` contains non-integer values.

    Name of wrong type:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> x = Field(name=ELEMENT_ID, data_type="INTEGER")
    >>> _ = gpkg.create_table(MAPPING_TABLE, fields=(x, y), overwrite=True)
    >>> with gpkg.connection as connection:
    ...     _ = connection.execute(
    ...         f"INSERT INTO {MAPPING_TABLE}"
    ...         f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES (1, 2)"
    ...     )
    >>> gpkg.connection.close()
    >>> read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    Traceback (most recent call last):
    ...
    TypeError: Column `element_name` of table `element_id2name` of geopackage \
`HydPy-H-Lahn/mpr_data/feature.gpkg` contains non-string values.

    Missing ID:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> y = Field(name=ELEMENT_NAME, data_type="TEXT", size=100)
    >>> _ = gpkg.create_table(MAPPING_TABLE, fields=(x, y), overwrite=True)
    >>> with gpkg.connection as connection:
    ...     for id_, name in ((1, '"one"'), ("NULL", '"two"'), (3, '"three"')):
    ...         _ = connection.execute(
    ...             f"INSERT INTO {MAPPING_TABLE}"
    ...             f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES ({id_}, {name})"
    ...         )
    >>> gpkg.connection.close()
    >>> with warn_later():
    ...     read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    {1: 'one', 3: 'three'}
    UserWarning: Column `element_id` of table `element_id2name` of geopackage \
`HydPy-H-Lahn/mpr_data/feature.gpkg` contains at least one missing value.

    Missing name:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> _ = gpkg.create_table(MAPPING_TABLE, fields=(x, y), overwrite=True)
    >>> with gpkg.connection as connection:
    ...     for id_, name in ((1, '"one"'), (2, "NULL"), (3, '"three"')):
    ...         _ = connection.execute(
    ...             f"INSERT INTO {MAPPING_TABLE}"
    ...             f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES ({id_}, {name})"
    ...         )
    >>> gpkg.connection.close()
    >>> with warn_later():
    ...     read_mapping_table("HydPy-H-Lahn/mpr_data/feature.gpkg")
    {1: 'one', 3: 'three'}
    UserWarning: Column `element_name` of table `element_id2name` of geopackage \
`HydPy-H-Lahn/mpr_data/feature.gpkg` contains at least one missing value.

    >>> reset_workingdir()
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Geopackage `{filepath}` does not exist.")
    gpkg = GeoPackage(filepath)
    try:
        table = gpkg.tables.get(MAPPING_TABLE)
        if table is None:
            raise TypeError(
                f"Geopackage `{filepath}` does not contain the required mapping table "
                f"`{MAPPING_TABLE}`."
            )
        for column in (ELEMENT_ID, ELEMENT_NAME):
            if column not in table.field_names:
                raise TypeError(
                    f"Geopackage `{filepath}` does not contain a column named "
                    f"`{column}`."
                )
    except BaseException as exc:
        gpkg.connection.close()
        raise exc

    element_id2name = {}
    cursor = table.select(fields=(ELEMENT_ID, ELEMENT_NAME))
    try:
        for element_id, element_name in cursor:
            if element_id is None:
                warnings.warn(
                    f"Column `{ELEMENT_ID}` of table `{MAPPING_TABLE}` of geopackage "
                    f"`{filepath}` contains at least one missing value."
                )
                continue
            if not isinstance(element_id, int):
                raise TypeError(
                    f"Column `{ELEMENT_ID}` of table `{MAPPING_TABLE}` of geopackage "
                    f"`{filepath}` contains non-integer values."
                )
            if element_name is None:
                warnings.warn(
                    f"Column `{ELEMENT_NAME}` of table `{MAPPING_TABLE}` of "
                    f"geopackage `{filepath}` contains at least one missing value."
                )
                continue
            if not isinstance(element_name, str):
                raise TypeError(
                    f"Column `{ELEMENT_NAME}` of table `{MAPPING_TABLE}` of "
                    f"geopackage `{filepath}` contains non-string values."
                )
            element_id2name[element_id] = element_name
    finally:
        cursor.close()
        gpkg.connection.close()

    return element_id2name
