"""Utilities for reading the raster, feature, and table data."""

from __future__ import annotations
import os.path
import warnings

from fudgeo.geopkg import GeoPackage
from numpy import array, float64, int64
from tifffile import TiffFile, TiffPage

from hydpy_mpr.source.constants import (
    ELEMENT_ID,
    ELEMENT_NAME,
    FEATURE_GPKG,
    MAPPING_TABLE,
)
from hydpy_mpr.source.typing_ import (
    Generic,
    Iterable,
    Literal,
    MappingTable,
    Matrix,
    MatrixBool,
    overload,
    TypeAlias,
    TypeVar,
)


TM = TypeVar("TM", float64, int64)


RasterFloat: TypeAlias = "Raster[float64]"
RasterInt: TypeAlias = "Raster[int64]"
RasterGroups: TypeAlias = dict[str, "RasterGroup"]


def read_mapping_table(*, dirpath: str) -> MappingTable:
    """Read the table for mapping element IDs to element names required when working
    with raster files.

    >>> from pprint import pprint
    >>> from fudgeo.geopkg import Field, GeoPackage
    >>> from hydpy.core.testtools import warn_later
    >>> from hydpy_mpr.source.constants import ELEMENT_ID, ELEMENT_NAME, MAPPING_TABLE
    >>> from hydpy_mpr.source.reading import read_mapping_table
    >>> from hydpy_mpr.testing import prepare_project

    >>> reset_workingdir = prepare_project("HydPy-H-Lahn")

    Everything okay:

    >>> pprint(read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data"))
    {np.int64(1): 'land_lahn_marb',
     np.int64(2): 'land_lahn_leun',
     np.int64(3): 'land_lahn_kalk',
     np.int64(4): 'land_dill_assl',
     np.int64(5): 'land_lahn_rest'}

    Missing file:

    >>> read_mapping_table(dirpath="HydPy-H-Lahn/mpr_date")
    Traceback (most recent call last):
    ...
    FileNotFoundError: Geopackage `HydPy-H-Lahn/mpr_date/feature.gpkg` does not exist.

    ID column missing:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> gpkg.tables[MAPPING_TABLE].drop()
    >>> gpkg.connection.close()
    >>> read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data")
    Traceback (most recent call last):
    ...
    TypeError: Geopackage `HydPy-H-Lahn/mpr_data/feature.gpkg` does not contain the \
required mapping table `element_id2name`.

    Name column missing:

    >>> gpkg = GeoPackage("HydPy-H-Lahn/mpr_data/feature.gpkg")
    >>> _ = gpkg.create_table(MAPPING_TABLE, fields=())
    >>> gpkg.connection.close()
    >>> read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data")
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
    >>> read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data")
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
    >>> read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data")
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
    ...     read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data")
    {np.int64(1): 'one', np.int64(3): 'three'}
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
    ...     read_mapping_table(dirpath="HydPy-H-Lahn/mpr_data")  # doctest: +ELLIPSIS
    {np.int64(1): 'one', np.int64(3): 'three'}
    UserWarning: Column `element_name` of table `element_id2name` of geopackage \
`HydPy-H-Lahn/mpr_data/feature.gpkg` contains at least one missing value.

    >>> reset_workingdir()
    """
    filepath = os.path.join(dirpath, FEATURE_GPKG)
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
            element_id2name[int64(element_id)] = element_name
    finally:
        cursor.close()
        gpkg.connection.close()

    return element_id2name


@overload
def read_geotiff(filepath: str, datatype: Literal["int"]) -> RasterInt: ...


@overload
def read_geotiff(filepath: str, datatype: Literal["float"]) -> RasterFloat: ...


def read_geotiff(
    filepath: str, datatype: Literal["int", "float"]
) -> RasterInt | RasterFloat:
    """

    >>> from hydpy_mpr.source.reading import read_geotiff
    >>> from hydpy_mpr.testing import prepare_project

    >>> reset_workingdir = prepare_project("HydPy-H-Lahn")

    >>> filepath = "HydPy-H-Lahn/mpr_data/raster/raster_5km/sand_mean_0_200_res5km.tif"
    >>> raster = read_geotiff(filepath, datatype="float")
    >>> raster.shape
    >>> raster

    >>> reset_workingdir()
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"GeoTiff `{filepath}` does not exist.")

    with TiffFile(filepath) as tiff:
        assert len(tiff.pages) == 1
        page = tiff.pages[0]
        assert isinstance(page, TiffPage)

        if datatype == "int":
            return Raster(
                values=array(tiff.asarray(), dtype=int64)[:-1, :-1],  # ToDo
                missingvalue=int64(page.tags[42113].value),
            )
        if datatype == "float":
            return Raster(
                values=array(tiff.asarray(), dtype=float64),
                missingvalue=float64(page.tags[42113].value),
            )


class Raster(Generic[TM]):
    values: Matrix[TM]
    missingvalue: TM
    shape: tuple[int, int]
    mask: MatrixBool

    def __init__(self, values: Matrix[TM], missingvalue: TM) -> None:
        self.values = values
        self.missingvalue = missingvalue
        self.shape = values.shape
        self.mask = values == missingvalue


def extract_tiffiles(filenames: Iterable[str]) -> list[str]:
    return [fn for fn in filenames if fn.rsplit(".")[-1] in ("tif", "tiff")]


class RasterGroup:

    data_rasters: dict[str, RasterFloat]
    id_raster: RasterInt
    shape: tuple[int, int]
    id2element: MappingTable
    mask: MatrixBool

    def __init__(self, projectpath: str, dirname: str) -> None:
        dirpath = os.path.join(projectpath, "raster", dirname)

        filenames = extract_tiffiles(os.listdir(dirpath))

        for idx, filename in enumerate(filenames):
            if filename.rsplit(".")[0] == ELEMENT_ID:
                filepath = os.path.join(dirpath, filename)
                self.id_raster = read_geotiff(filepath=filepath, datatype="int")
                self.shape = self.id_raster.shape
                break
        else:
            raise FileNotFoundError
        filenames.pop(idx)

        self.data_rasters = {}
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            raster = read_geotiff(filepath=filepath, datatype="float")
            if raster.shape != self.shape:
                raise RuntimeError(self.shape, raster.shape)
            self.data_rasters[filename.rsplit(".")[0]] = raster

        self.id2element = read_mapping_table(dirpath=projectpath)


def read_rastergroups(projectpath: str) -> RasterGroups:
    raster_groups: RasterGroups = {}
    dirpath = os.path.join(projectpath, "raster")
    for subdirname in os.listdir(dirpath):
        subdirpath = os.path.join(dirpath, subdirname)
        if os.path.isdir(subdirpath):
            raster_groups[subdirname] = RasterGroup(
                projectpath=projectpath, dirname=subdirname
            )
    return raster_groups
