"""Utilities for reading the raster, feature, and table data."""

from __future__ import annotations
import dataclasses
import os
import warnings

from fudgeo import geopkg
from hydpy.core import objecttools
import numpy
import tifffile

from hydpy_mpr.source import constants
from hydpy_mpr.source.constants import ELEMENT_ID, ELEMENT_NAME
from hydpy_mpr.source.typing_ import *


TypeVarNumber = TypeVar("TypeVarNumber", float64, int64)


def _get_path_geopackage(*, mprpath: DirpathMPRData) -> FilepathGeopackage:
    filepath = os.path.join(mprpath, constants.FEATURE_GPKG)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Geopackage `{filepath}` does not exist.")
    return FilepathGeopackage(filepath)


def read_mapping_table(*, mprpath: DirpathMPRData) -> MappingTable:
    """Read the table for mapping element IDs to element names required when working
    with raster files."""

    def _column_contains(column: str) -> str:
        return (
            f"Column `{column}` of table `{constants.MAPPING_TABLE}` of geopackage "
            f"`{filepath}` contains"
        )

    filepath = _get_path_geopackage(mprpath=mprpath)
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
def read_geotiff(*, filepath: str, integer: Literal[True]) -> RasterInt: ...


@overload
def read_geotiff(
    *, filepath: str, integer: Literal[False] = False
) -> RasterFloat | RasterInt: ...


def read_geotiff(  # pylint: disable=inconsistent-return-statements
    *, filepath: str, integer: bool = False
) -> RasterFloat | RasterInt:
    """

    >>> from hydpy_mpr.source.reading import read_geotiff
    >>> from hydpy_mpr.testing import prepare_project

    >>> reset_workingdir = prepare_project("HydPy-H-Lahn")

    >>> filepath = "HydPy-H-Lahn/mpr_data/raster/raster_5km/sand_mean_0_200_res5km.tif"
    >>> raster = read_geotiff(filepath=filepath)
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
        dtype = tiff.pages[0].dtype
        if dtype is None:
            warnings.warn(
                f"The data type of tiff file `{filepath}` cannot be detected.  "
                f"Assuming `{'integer' if integer else 'float'}`."
            )
        elif integer and not numpy.isdtype(dtype, "integral"):
            warnings.warn(
                f"The data type of tiff file `{filepath}` is `{dtype.name}` but "
                f"integer values are expected."
            )
        if integer or ((dtype is not None) and numpy.isdtype(dtype, "integral")):
            return RasterInt(
                values=numpy.array(tiff.asarray(), dtype=int64),
                missingvalue=int64(page.tags[42113].value),
            )
        values = numpy.array(tiff.asarray(), dtype=float64)
        missingvalue = float64(page.tags[42113].value)
        if not numpy.isnan(missingvalue):
            values[values == missingvalue] = numpy.nan
        return RasterFloat(values=values)


@dataclasses.dataclass(kw_only=True)
class Data(Generic[TypeVarNumber]):

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
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


@dataclasses.dataclass(kw_only=True, eq=False)
class Raster(Data[TypeVarNumber]):
    values: Matrix[TypeVarNumber]
    shape: tuple[int, int] = dataclasses.field(init=False)
    mask: MatrixBool = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.shape = self.values.shape


@dataclasses.dataclass(kw_only=True, eq=False)
class RasterInt(Raster[int64]):

    missingvalue: int64

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.mask = self.values != self.missingvalue


@dataclasses.dataclass(kw_only=True, eq=False)
class RasterFloat(Raster[float64]):

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.mask = ~numpy.isnan(self.values)


@dataclasses.dataclass(kw_only=True, eq=False)
class Attribute(Data[TypeVarNumber]):
    values: Vector[TypeVarNumber]
    shape: int = dataclasses.field(init=False)
    mask: VectorBool = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.shape = self.values.shape[0]


@dataclasses.dataclass(kw_only=True, eq=False)
class AttributeInt(Attribute[int64]):

    missingvalue: int64

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.mask = self.values != self.missingvalue

    @classmethod
    def from_vector(cls, vector: Vector[numpy.object_], /) -> Self:
        vector = vector.copy()
        idxs = vector != None  # pylint: disable=singleton-comparison
        missingvalue = int64(min(int(numpy.min(vector[idxs])) - 1, -9999))
        vector[~idxs] = missingvalue
        return cls(values=vector.astype(int64), missingvalue=missingvalue)


@dataclasses.dataclass(kw_only=True, eq=False)
class AttributeFloat(Attribute[float64]):

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.mask = ~numpy.isnan(self.values)

    @classmethod
    def from_vector(cls, vector: Vector[numpy.object_], /) -> Self:
        vector = vector.copy()
        vector[vector == None] = numpy.nan  # pylint: disable=singleton-comparison
        return cls(values=vector.astype(float64))


def _extract_tiffiles(filenames: Iterable[str]) -> list[str]:
    return [fn for fn in filenames if fn.rsplit(".")[-1] in ("tif", "tiff")]


@dataclasses.dataclass(kw_only=True)
class RasterGroup:

    mprpath: DirpathMPRData
    name: NameRasterGroup
    data_rasters: dict[str, RasterFloat | RasterInt] = dataclasses.field(init=False)
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
                self.element_raster = read_geotiff(filepath=filepath, integer=True)
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
                self.subunit_raster = read_geotiff(filepath=filepath, integer=True)
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
            raster = read_geotiff(filepath=filepath)
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


@dataclasses.dataclass(kw_only=True)
class FeatureClass:
    mprpath: DirpathMPRData
    name: NameFeatureClass
    attribute_names: tuple[NameAttribute, ...]
    element_attribute: AttributeInt = dataclasses.field(init=False)
    subunit_attribute: AttributeInt = dataclasses.field(init=False)
    size_attribute: AttributeFloat = dataclasses.field(init=False)
    data_attribute: dict[NameAttribute, AttributeInt | AttributeFloat] = (
        dataclasses.field(init=False)
    )

    nmb_features: int = dataclasses.field(init=False)

    def __post_init__(self) -> None:

        filepath = _get_path_geopackage(mprpath=self.mprpath)
        gpkg = geopkg.GeoPackage(filepath)

        try:

            featureclass = gpkg.feature_classes.get(self.name)
            if featureclass is None:
                raise TypeError(
                    f"Geopackage `{filepath}` does not contain the required feature "
                    f"class `{self.name}`."
                )

            # Determine the relevant headers (field names), typically something like
            # ["element_id", "subunit_id", "Area", "field_capacity", "landuse"]
            headers = self._prepare_headers(
                filepath=filepath, name=self.name, field_names=featureclass.field_names
            )
            self._append_size_header(
                filepath=filepath,
                name=self.name,
                headers=headers,
                geometry_type=featureclass.geometry_type,
            )
            headers.extend(self.attribute_names)

            # Determine the corresponding types, for the above example something like
            # [int64, int64, float64, float64, int64]
            types = self._get_types(
                filepath=filepath,
                name=self.name,
                headers=headers,
                field_names=featureclass.field_names,
                fields=featureclass.fields,
            )

            # Query the relevant data:
            try:
                cursor = featureclass.select(fields=headers, include_geometry=False)
                data = numpy.asarray(cursor.fetchall(), dtype=object)
            finally:
                cursor.close()

        finally:
            gpkg.connection.close()

        self.element_attribute = AttributeInt.from_vector(data[:, 0])
        if delta := constants.SUBUNIT_ID in headers:
            self.subunit_attribute = AttributeInt.from_vector(data[:, 1])
        self.size_attribute = AttributeFloat.from_vector(data[:, 1 + delta])

        self.data_attribute = {}
        for idx, (header, type_) in enumerate(
            zip(headers[1 + delta :], types[1 + delta :])
        ):
            self.data_attribute[header] = type_.from_vector(data[:, 1 + delta + idx])

        self.nmb_features = self.element_attribute.shape

    @staticmethod
    def _prepare_headers(
        filepath: FilepathGeopackage, name: NameFeatureClass, field_names: list[str]
    ) -> list[NameAttribute]:
        headers = [NameAttribute(constants.ELEMENT_ID)]
        if constants.SUBUNIT_ID in field_names:
            headers.append(NameAttribute(constants.SUBUNIT_ID))
        else:
            warnings.warn(
                f"Feature class `{name}` of geopackage `{filepath}` does not contain "
                f"a `{constants.SUBUNIT_ID}` attribute."
            )
        return headers

    @staticmethod
    def _append_size_header(
        *,
        filepath: FilepathGeopackage,
        name: NameFeatureClass,
        headers: list[NameAttribute],
        geometry_type: str | None,
    ) -> None:

        polygontypes = ("POLYGON", "MULTIPOLYGON")
        linetypes = ("LINESTRING", "MULTILINESTRING")

        if geometry_type is None:
            raise TypeError(
                f"Feature class `{name}` of geopackage `{filepath}` does not specify "
                f"its geometry type."
            )
        geometry_type = geometry_type.upper()
        if geometry_type in polygontypes:
            headers.append(NameAttribute(constants.Size.AREA))
        elif geometry_type in linetypes:
            headers.append(NameAttribute(constants.Size.LENGTH))
        else:
            raise TypeError(
                f"Feature class `{name}` of geopackage `{filepath}` defines the "
                f"geometry type `{geometry_type}` but only the types "
                f"{objecttools.enumeration(polygontypes + linetypes)} are supported."
            )

    @staticmethod
    def _get_types(
        filepath: FilepathGeopackage,
        name: NameFeatureClass,
        headers: list[NameAttribute],
        field_names: list[str],
        fields: list[geopkg.Field],
    ) -> list[type[AttributeInt | AttributeFloat]]:

        integers = ("TINYINT", "SMALLINT", "MEDIUMINT", "INTEGER", "INT")
        floats = ("FLOAT", "DOUBLE", "REAL")

        header2idx = {}
        for header in headers:
            if header not in field_names:
                raise TypeError(
                    f"Feature class `{name}` of geopackage `{filepath}` does not "
                    f"provide an attribute named `{header}`."
                )
            header2idx[header] = field_names.index(header)

        types: list[type[AttributeInt | AttributeFloat]] = []
        for header in headers:

            field = fields[header2idx[header]]
            datatype = field.data_type.upper()

            if header in constants.Size:
                types.append(AttributeFloat)
                if datatype not in floats:
                    available_types = objecttools.enumeration(floats, conjunction="or")
                    warnings.warn(
                        f"The data type of attribute `{header}` of feature class "
                        f"`{name}` of geopackage `{filepath}` is `{field.data_type}` "
                        f"but {available_types} is expected."
                    )
            elif datatype in integers:
                types.append(AttributeInt)
            elif header in (constants.ELEMENT_ID, constants.SUBUNIT_ID):
                types.append(AttributeInt)
                available_types = objecttools.enumeration(integers, conjunction="or")
                warnings.warn(
                    f"The data type of attribute `{header}` of feature class `{name}` "
                    f"of geopackage `{filepath}` is `{field.data_type}` but "
                    f"{available_types} is expected."
                )
            else:
                types.append(AttributeFloat)
                if datatype not in floats:
                    available_types = objecttools.enumeration(integers + floats)
                    warnings.warn(
                        f"The data type of attribute `{header}` of feature class "
                        f"`{name}` of geopackage `{filepath}` is `{field.data_type}` "
                        f"but only the types {available_types} are supported."
                    )

        return types


@dataclasses.dataclass(kw_only=True)
class RasterGroups:
    mprpath: DirpathMPRData
    groups: dict[str, RasterGroup] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.groups = {}

    def __getitem__(self, name: NameRasterGroup) -> RasterGroup:
        if name not in self.groups:
            self.groups[name] = RasterGroup(mprpath=self.mprpath, name=name)
        return self.groups[name]
