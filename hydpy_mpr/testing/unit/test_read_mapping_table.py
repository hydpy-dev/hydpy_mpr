# pylint: disable=missing-docstring, unused-argument

from os.path import join
from re import escape

from fudgeo.geopkg import Field, GeoPackage
from numpy import int64
from pytest import raises, warns

from hydpy_mpr.source.constants import ELEMENT_ID, ELEMENT_NAME, MAPPING_TABLE
from hydpy_mpr.source.reading import read_mapping_table


DIRPATH_PROJECT = "HydPy-H-Lahn"
DIRPATH_MPR_DATA = join(DIRPATH_PROJECT, "mpr_data")
FILENAME_FEATURE = "feature.gpkg"
DIRPATH_FEATURE = join("HydPy-H-Lahn", "mpr_data", FILENAME_FEATURE)


def modify_table(*fields: Field) -> GeoPackage:
    gpkg = GeoPackage(DIRPATH_FEATURE)
    gpkg.create_table(MAPPING_TABLE, fields=fields, overwrite=True)
    return gpkg


def test_everything_okay(fixture_project: None) -> None:
    assert read_mapping_table(dirpath=DIRPATH_MPR_DATA) == {
        int64(1): "land_lahn_marb",
        int64(2): "land_lahn_leun",
        int64(3): "land_lahn_kalk",
        int64(4): "land_dill_assl",
        int64(5): "land_lahn_rest",
    }


def test_missing_file(tmp_path: str) -> None:
    with raises(FileNotFoundError) as info:
        read_mapping_table(dirpath=tmp_path)
    assert str(info.value) == (
        f"Geopackage `{join(tmp_path, FILENAME_FEATURE)}` does not exist."
    )


def test_missing_table(fixture_project: None) -> None:
    gpkg = GeoPackage(DIRPATH_FEATURE)
    gpkg.tables[MAPPING_TABLE].drop()
    gpkg.connection.close()
    with raises(TypeError) as info:
        read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        f"Geopackage `{DIRPATH_FEATURE}` does not contain the required mapping table "
        f"`element_id2name`."
    )


def test_missing_column(fixture_project: None) -> None:
    modify_table().connection.close()
    with raises(TypeError) as info:
        read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        f"Geopackage `{DIRPATH_FEATURE}` does not contain a column named `element_id`."
    )


def test_missing_id(fixture_project: None) -> None:
    gpkg = modify_table(
        Field(name=ELEMENT_ID, data_type="INTEGER"),
        Field(name=ELEMENT_NAME, data_type="TEXT", size=100),
    )
    with gpkg.connection as connection:
        for id_, name in ((1, '"one"'), ("NULL", '"two"'), (3, '"three"')):
            _ = connection.execute(
                f"INSERT INTO {MAPPING_TABLE}"
                f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES ({id_}, {name})"
            )
    gpkg.connection.close()
    with warns(
        UserWarning,
        match=escape(
            "Column `element_id` of table `element_id2name` of geopackage "
            f"`{DIRPATH_FEATURE}` contains at least one missing value."
        ),
    ):
        table = read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert table == {int64(1): "one", int64(3): "three"}


def test_missing_name(fixture_project: None) -> None:
    gpkg = modify_table(
        Field(name=ELEMENT_ID, data_type="INTEGER"),
        Field(name=ELEMENT_NAME, data_type="TEXT", size=100),
    )
    with gpkg.connection as connection:
        for id_, name in ((1, '"one"'), (2, "NULL"), (3, '"three"')):
            _ = connection.execute(
                f"INSERT INTO {MAPPING_TABLE}"
                f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES ({id_}, {name})"
            )
    gpkg.connection.close()
    with warns(
        UserWarning,
        match=escape(
            "Column `element_name` of table `element_id2name` of geopackage "
            f"`{DIRPATH_FEATURE}` contains at least one missing value."
        ),
    ):
        table = read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert table == {int64(1): "one", int64(3): "three"}


def test_wrong_id_type(fixture_project: None) -> None:
    gpkg = modify_table(
        Field(name=ELEMENT_ID, data_type="DOUBLE"),
        Field(name=ELEMENT_NAME, data_type="TEXT", size=100),
    )
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {MAPPING_TABLE}"
            f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES (1.5, 'test')"
        )
    gpkg.connection.close()
    with raises(TypeError) as info:
        read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        "Column `element_id` of table `element_id2name` of geopackage "
        f"`{DIRPATH_FEATURE}` contains non-integer values."
    )


def test_wrong_name_type(fixture_project: None) -> None:
    gpkg = modify_table(
        Field(name=ELEMENT_ID, data_type="INTEGER"),
        Field(name=ELEMENT_NAME, data_type="DOUBLE"),
    )
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {MAPPING_TABLE}"
            f"({ELEMENT_ID}, {ELEMENT_NAME}) VALUES (1, 1.5)"
        )
    gpkg.connection.close()
    with raises(TypeError) as info:
        read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        "Column `element_name` of table `element_id2name` of geopackage "
        f"`{DIRPATH_FEATURE}` contains non-string values."
    )
