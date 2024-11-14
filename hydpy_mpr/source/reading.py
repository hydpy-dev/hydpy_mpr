"""Utilities for reading the raster, feature, and table data."""

from __future__ import annotations
import dataclasses
import os
import warnings

from fudgeo import geopkg
import numpy
import tifffile

from hydpy_mpr.source import constants
from hydpy_mpr.source.constants import ELEMENT_ID, ELEMENT_NAME
from hydpy_mpr.source.typing_ import *


TM = TypeVar("TM", float64, int64)


def read_mapping_table(*, mprpath: str) -> MappingTable:
    """Read the table for mapping element IDs to element names required when working
    with raster files."""

    filepath = os.path.join(mprpath, constants.FEATURE_GPKG)

    def _column_contains(column: str) -> str:
        return (
            f"Column `{column}` of table `{constants.MAPPING_TABLE}` of geopackage "
            f"`{filepath}` contains"
        )

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Geopackage `{filepath}` does not exist.")
    gpkg = geopkg.GeoPackage(filepath)
    try:
        table = gpkg.tables.get(constants.MAPPING_TABLE)
        if table is None:
            raise TypeError(
                f"Geopackage `{filepath}` does not contain the required mapping table "
                f"`{constants.MAPPING_TABLE}`."
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
                    f"{_column_contains(ELEMENT_ID)} at least one missing value."
                )
                continue
            if not isinstance(element_id, int):
                raise TypeError(f"{_column_contains(ELEMENT_ID)} non-integer values.")
            if element_name is None:
                warnings.warn(
                    f"{_column_contains(ELEMENT_NAME)} at least one missing value."
                )
                continue
            if not isinstance(element_name, str):
                raise TypeError(f"{_column_contains(ELEMENT_NAME)} non-string values.")
            element_id2name[int64(element_id)] = element_name
    finally:
        cursor.close()
        gpkg.connection.close()

    return element_id2name


@overload
def read_geotiff(filepath: str, datatype: Literal["int"]) -> RasterInt: ...


@overload
def read_geotiff(filepath: str, datatype: Literal["float"]) -> RasterFloat: ...


def read_geotiff(  # pylint: disable=inconsistent-return-statements
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

    with tifffile.TiffFile(filepath) as tiff:
        assert len(tiff.pages), (
            f"HydPy-MPR supports only single-page tiff files, but `{filepath}` "
            f"contains `{len(tiff.pages)}` pages."
        )
        page = tiff.pages[0]
        assert isinstance(page, tifffile.TiffPage), (
            f"HydPy-MPR supports only tiff files containing tiff pages, but "
            f"`{filepath}` contains at least one tiff frame."
        )
        # pylint: disable=unexpected-keyword-arg
        if datatype == "int":
            return RasterInt(
                values=numpy.array(tiff.asarray(), dtype=int64),
                missingvalue=int64(page.tags[42113].value),
            )
        if datatype == "float":
            values = numpy.array(tiff.asarray(), dtype=float64)
            missingvalue = float64(page.tags[42113].value)
            if not numpy.isnan(missingvalue):
                values[values == missingvalue] = numpy.nan
            return RasterFloat(values=values)


@dataclasses.dataclass
class Raster(Generic[TM]):
    values: Matrix[TM]
    shape: tuple[int, int] = dataclasses.field(init=False)
    mask: MatrixBool = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.shape = self.values.shape

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Raster):
            fields_self = tuple(field.name for field in dataclasses.fields(self))
            fields_other = tuple(field.name for field in dataclasses.fields(other))
            if fields_self != fields_other:
                return False
            for field in fields_self:
                if field in ("values", "mask"):
                    if not numpy.array_equal(
                        getattr(self, field), getattr(other, field), equal_nan=True
                    ):
                        return False
                else:
                    if getattr(self, field) != getattr(other, field):
                        return False
            return True
        return False


@dataclasses.dataclass
class RasterInt(Raster[int64]):

    missingvalue: int64

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.mask = self.values != self.missingvalue

    @override
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


@dataclasses.dataclass
class RasterFloat(Raster[float64]):

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.mask = ~numpy.isnan(self.values)

    @override
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


def _extract_tiffiles(filenames: Iterable[str]) -> list[str]:
    return [fn for fn in filenames if fn.rsplit(".")[-1] in ("tif", "tiff")]


@dataclasses.dataclass
class RasterGroup:

    mprpath: str
    name: str
    data_rasters: dict[str, RasterFloat] = dataclasses.field(init=False)
    element_raster: RasterInt = dataclasses.field(init=False)
    subunit_raster: RasterInt = dataclasses.field(init=False)
    shape: tuple[int, int] = dataclasses.field(init=False)
    id2element: MappingTable = dataclasses.field(init=False)

    def __post_init__(self) -> None:

        dirpath = os.path.join(self.mprpath, constants.RASTER, self.name)
        if not os.path.exists(dirpath):
            raise FileNotFoundError(
                f"The requested raster group directory `{dirpath}` does not exist."
            )
        filenames = _extract_tiffiles(os.listdir(dirpath))

        # Read the element ID raster:
        for idx, filename in enumerate(tuple(filenames)):
            if filename.rsplit(".")[0] == constants.ELEMENT_ID:
                filepath = os.path.join(dirpath, filename)
                self.element_raster = read_geotiff(filepath=filepath, datatype="int")
                self.shape = self.element_raster.shape
                filenames.pop(idx)
                break
        else:
            raise FileNotFoundError(
                f"The raster group directory `{dirpath}` does not contain an "
                f"`{constants.ELEMENT_ID}` raster file."
            )

        # Read the subunit ID raster:
        for idx, filename in enumerate(tuple(filenames)):
            if filename.rsplit(".")[0] == constants.SUBUNIT_ID:
                filepath = os.path.join(dirpath, filename)
                self.subunit_raster = read_geotiff(filepath=filepath, datatype="int")
                self._check_shape(self.subunit_raster.shape, filename)
                filenames.pop(idx)
                break
        else:
            warnings.warn(
                f"The raster group directory `{dirpath}` does not contain a "
                f"`{constants.SUBUNIT_ID}` raster file."
            )

        # Read the geodata rasters:
        self.data_rasters = {}
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            raster = read_geotiff(filepath=filepath, datatype="float")
            self._check_shape(raster.shape, filename)
            self.data_rasters[filename.rsplit(".")[0]] = raster

        # Read the mapping table:
        self.id2element = read_mapping_table(mprpath=self.mprpath)

    def _check_shape(self, shape: tuple[int, int], filename: str, /) -> None:
        if self.shape != shape:
            raise TypeError(
                f"Raster group `{self.name}` is inconsistent: shape `{self.shape}` of "
                f"raster `{constants.ELEMENT_ID}` conflicts with shape `{shape}` of "
                f"raster `{filename}`."
            )


@dataclasses.dataclass
class RasterGroups:
    mprpath: str
    groups: dict[str, RasterGroup] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.groups = {}

    def __getitem__(self, name: str) -> RasterGroup:
        if name not in self.groups:
            self.groups[name] = RasterGroup(mprpath=self.mprpath, name=name)
        return self.groups[name]
