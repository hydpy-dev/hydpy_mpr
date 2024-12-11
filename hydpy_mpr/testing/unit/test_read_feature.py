# pylint: disable=missing-docstring, protected-access

from __future__ import annotations
import os
import re

from fudgeo import geopkg
import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source import constants
from hydpy_mpr.source.typing_ import *


def test_read_features_everything_okay(
    arrange_project: None,  # pylint: disable=unused-argument
    dirpath_mpr_data: DirpathMPRData,
    name_feature_class: NameProvider,
    name_attribute_kf: NameDataset,
) -> None:
    f = hydpy_mpr.FeatureClass(
        mprpath=dirpath_mpr_data, name=name_feature_class, datasets=(name_attribute_kf,)
    )
    e = f.element_id

    assert f.shape == e.shape == 1591

    assert isinstance(e, hydpy_mpr.AttributeInt)
    assert numpy.all(e.values[:3] == (5, 3, 5))
    assert numpy.min(e.values) == 1
    assert numpy.max(e.values) == 5

    s = f.subunit_id
    assert isinstance(s, hydpy_mpr.AttributeInt)
    assert numpy.all(s.values[:3] == (1, 0, 0))
    assert numpy.min(s.values) == 0
    assert numpy.max(s.values) == 11

    a = f.size
    assert isinstance(a, hydpy_mpr.AttributeFloat)
    assert numpy.all(
        a.values[:3]
        == pytest.approx([10.41044807434082, 7795.1435546875, 57755.77734375])
    )
    assert numpy.min(a.values) == pytest.approx(0.9527015089988708)
    assert numpy.max(a.values) == pytest.approx(232333792.0)

    k = f.data[name_attribute_kf]
    assert isinstance(k, hydpy_mpr.AttributeInt)
    assert numpy.all(k.values[:3] == (2, 3, 3))
    assert numpy.min(k.values) == 2.0
    assert numpy.max(k.values) == 12.0


def test_read_features_missing_geopackage(tmp_path: DirpathMPRData) -> None:
    with pytest.raises(FileNotFoundError) as info:
        hydpy_mpr.FeatureClass(mprpath=tmp_path, name=NameProvider(""), datasets=())
    assert str(info.value) == (
        f"Geopackage `{os.path.join(tmp_path, constants.FEATURE_GPKG)}` does not exist."
    )


def test_read_features_missing_feature_class(
    arrange_project: None,  # pylint: disable=unused-argument
    dirpath_mpr_data: DirpathMPRData,
    filepath_feature: FilepathGeopackage,
) -> None:
    with pytest.raises(TypeError) as info:
        hydpy_mpr.FeatureClass(
            mprpath=dirpath_mpr_data, name=NameProvider("wrong"), datasets=()
        )
    assert str(info.value) == (
        f"Geopackage `{filepath_feature}` does not contain the required feature class "
        "`wrong`."
    )


def test_read_features_subunit_id_available() -> None:
    headers = hydpy_mpr.FeatureClass._prepare_headers(
        filepath=FilepathGeopackage("path_geopackage"),
        name=NameProvider("name_featureclass"),
        field_names=["x", constants.SUBUNIT_ID, "y", constants.ELEMENT_ID, "z"],
    )
    assert headers == [constants.ELEMENT_ID, constants.SUBUNIT_ID]


def test_read_features_subunit_id_missing() -> None:
    with pytest.warns(
        UserWarning,
        match=re.escape(
            f"Feature class `name_featureclass` of geopackage `path_geopackage` "
            f"does not contain a `{constants.SUBUNIT_ID}` attribute."
        ),
    ):
        headers = hydpy_mpr.FeatureClass._prepare_headers(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            field_names=["x", constants.ELEMENT_ID, "y"],
        )
    assert headers == [constants.ELEMENT_ID]


@pytest.mark.parametrize(
    "geometry_type, expected",
    (
        ("POLYGON", constants.Size.AREA),
        ("MULTIPOLYGON", constants.Size.AREA),
        ("LINESTRING", constants.Size.LENGTH),
        ("MULTILINESTRING", constants.Size.LENGTH),
    ),
)
def test_read_features_geometry_type_everything_okay(
    geometry_type: str, expected: constants.Size
) -> None:
    headers = cast(list[NameDataset], ["x", "y"])
    hydpy_mpr.FeatureClass._append_size_header(
        filepath=FilepathGeopackage("path_geopackage"),
        name=NameProvider("name_featureclass"),
        headers=headers,
        geometry_type=geometry_type,
    )
    assert headers == ["x", "y", expected]


def test_read_features_missing_geometry_type() -> None:
    with pytest.raises(TypeError) as info:
        hydpy_mpr.FeatureClass._append_size_header(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            headers=[],
            geometry_type=None,
        )
    assert str(info.value) == (
        "Feature class `name_featureclass` of geopackage `path_geopackage` does not "
        "specify its geometry type."
    )


def test_read_features_geometry_type_unsupported() -> None:
    with pytest.raises(TypeError) as info:
        hydpy_mpr.FeatureClass._append_size_header(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            headers=[],
            geometry_type="GEOMETRYCOLLECTION",
        )
    assert str(info.value) == (
        "Feature class `name_featureclass` of geopackage `path_geopackage` defines "
        "the geometry type `GEOMETRYCOLLECTION` but only the types POLYGON, "
        "MULTIPOLYGON, LINESTRING, and MULTILINESTRING are supported."
    )


def test_read_features_missing_attribute() -> None:
    with pytest.raises(TypeError) as info:
        hydpy_mpr.FeatureClass._get_types(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            headers=cast(list[NameDataset], ["x", "y", "z"]),
            field_names=["z", "x"],
            fields=[],
        )
    assert str(info.value) == (
        "Feature class `name_featureclass` of geopackage `path_geopackage` does not "
        "provide an attribute named `y`."
    )


def test_read_features_types_okay() -> None:
    i4, i5 = constants.SUBUNIT_ID, constants.ELEMENT_ID
    f3 = constants.Size.AREA
    field_names = ["c", "f1", "f2", f3, i4, i5, "i6", "i7", "i8"]
    fields = [geopkg.Field(name=n, data_type="COMPLEX") for n in field_names]
    fields[1].data_type = "FLOAT"
    fields[2].data_type = "DOUBLE"
    fields[3].data_type = "REAL"
    fields[4].data_type = "TINYINT"
    fields[5].data_type = "SMALLINT"
    fields[6].data_type = "MEDIUMINT"
    fields[7].data_type = "INT"
    fields[8].data_type = "INTEGER"
    types = hydpy_mpr.FeatureClass._get_types(
        filepath=FilepathGeopackage("path_geopackage"),
        name=NameProvider("name_featureclass"),
        headers=cast(list[NameDataset], [i5, i4, f3, "i6", "i7", "i8", "f1", "f2"]),
        field_names=field_names,
        fields=fields,
    )
    assert types == [
        hydpy_mpr.AttributeInt,
        hydpy_mpr.AttributeInt,
        hydpy_mpr.AttributeFloat,
        hydpy_mpr.AttributeInt,
        hydpy_mpr.AttributeInt,
        hydpy_mpr.AttributeInt,
        hydpy_mpr.AttributeFloat,
        hydpy_mpr.AttributeFloat,
    ]


def test_read_features_id_should_be_int() -> None:
    with pytest.warns(
        UserWarning,
        match=(
            f"The data type of attribute `{constants.ELEMENT_ID}` of feature class "
            f"`name_featureclass` of geopackage `path_geopackage` is `FLOAT` but "
            f"TINYINT, SMALLINT, MEDIUMINT, INTEGER, or INT is expected."
        ),
    ):
        field_names = ["a", "x", "y", constants.ELEMENT_ID, "z"]
        fields = [geopkg.Field(name=n, data_type="int") for n in field_names]
        fields[3].data_type = "FLOAT"
        hydpy_mpr.FeatureClass._get_types(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            headers=cast(list[NameDataset], [constants.ELEMENT_ID, "x", "y", "z"]),
            field_names=field_names,
            fields=fields,
        )


def test_read_features_size_should_be_float() -> None:
    with pytest.warns(
        UserWarning,
        match=(
            "The data type of attribute `Area` of feature class `name_featureclass` "
            "of geopackage `path_geopackage` is `INTEGER` but FLOAT, DOUBLE, or REAL "
            "is expected."
        ),
    ):
        field_names = ["a", "x", "y", constants.ELEMENT_ID, constants.Size.AREA, "z"]
        fields = [geopkg.Field(name=n, data_type="float") for n in field_names]
        fields[4].data_type = "INTEGER"
        hydpy_mpr.FeatureClass._get_types(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            headers=cast(
                list[NameDataset],
                [constants.ELEMENT_ID, constants.Size.AREA, "x", "y", "z"],
            ),
            field_names=field_names,
            fields=fields,
        )


def test_read_features_geodata_should_be_int_or_float() -> None:
    with pytest.warns(
        UserWarning,
        match=(
            "The data type of attribute `y` of feature class `name_featureclass` of "
            "geopackage `path_geopackage` is `COMPLEX` but only the types TINYINT, "
            "SMALLINT, MEDIUMINT, INTEGER, INT, FLOAT, DOUBLE, and REAL are supported."
        ),
    ):
        field_names = ["a", "x", "y", constants.ELEMENT_ID, "z"]
        fields = [geopkg.Field(name=n, data_type="int") for n in field_names]
        fields[2].data_type = "COMPLEX"
        hydpy_mpr.FeatureClass._get_types(
            filepath=FilepathGeopackage("path_geopackage"),
            name=NameProvider("name_featureclass"),
            headers=cast(list[NameDataset], [constants.ELEMENT_ID, "x", "y", "z"]),
            field_names=field_names,
            fields=fields,
        )


def test_read_features_missing_values(
    arrange_project: None,  # pylint: disable=unused-argument
    dirpath_mpr_data: DirpathMPRData,
    filepath_feature: FilepathGeopackage,
    name_feature_class: NameProvider,
    name_attribute_kf: NameDataset,
) -> None:
    gpkg = geopkg.GeoPackage(filepath_feature)
    f = gpkg.feature_classes.get(name_feature_class)
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {name_feature_class} "
            f"({', '.join(f.field_names)}) "
            f"VALUES ({', '.join(len(f.field_names) * ['NULL'])})"
        )
    gpkg.connection.close()

    f = hydpy_mpr.FeatureClass(
        mprpath=dirpath_mpr_data, name=name_feature_class, datasets=(name_attribute_kf,)
    )
    e = f.element_id

    assert f.shape == e.shape == 1592

    assert isinstance(e, hydpy_mpr.AttributeInt)
    assert e.missingvalue == int64(-9999)
    assert numpy.sum(e.mask) == 1591
    assert numpy.all(e.values[:3] == (5, 3, 5))
    assert numpy.min(e.values) == -9999
    assert numpy.min(e.values[e.mask]) == 1

    a = f.size
    assert isinstance(a, hydpy_mpr.AttributeFloat)
    assert numpy.all(
        a.values[:3]
        == pytest.approx([10.41044807434082, 7795.1435546875, 57755.77734375])
    )
    assert numpy.isnan(numpy.min(a.values))
    assert numpy.min(a.values[a.mask]) == pytest.approx(0.9527015089988708)


def test_attribute_float_missing_values() -> None:
    a = hydpy_mpr.AttributeFloat.from_vector(numpy.array([1, None, 3.5], dtype=object))
    assert numpy.array_equal(a.values, [1.0, numpy.nan, 3.5], equal_nan=True)
    assert numpy.array_equal(a.mask, [True, False, True])


def test_attribute_int_default_missing_value() -> None:
    a = hydpy_mpr.AttributeInt.from_vector(numpy.array([1, None, 3.5], dtype=object))
    assert a.missingvalue == -9999
    assert numpy.array_equal(a.values, [1, -9999, 3])
    assert numpy.array_equal(a.mask, [True, False, True])


def test_attribute_int_adjusted_missing_value() -> None:
    a = hydpy_mpr.AttributeInt.from_vector(numpy.array([1, None, -10000], dtype=object))
    assert a.missingvalue == -10001
    assert numpy.array_equal(a.values, [1, -10001, -10000])
    assert numpy.array_equal(a.mask, [True, False, True])
