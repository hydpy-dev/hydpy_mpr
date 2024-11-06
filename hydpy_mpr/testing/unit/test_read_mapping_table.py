# pylint: disable=missing-docstring, unused-argument

from __future__ import annotations
import os
import re

from fudgeo import geopkg
import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


DIRPATH_PROJECT = "HydPy-H-Lahn"
DIRPATH_MPR_DATA = os.path.join(DIRPATH_PROJECT, "mpr_data")
FILENAME_FEATURE = "feature.gpkg"
DIRPATH_FEATURE = os.path.join("HydPy-H-Lahn", "mpr_data", FILENAME_FEATURE)


def modify_table(*fields: geopkg.Field) -> geopkg.GeoPackage:
    gpkg = geopkg.GeoPackage(DIRPATH_FEATURE)
    gpkg.create_table(constants.MAPPING_TABLE, fields=fields, overwrite=True)
    return gpkg


def test_everything_okay(fixture_project: None) -> None:
    assert reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA) == {
        int64(1): "land_lahn_marb",
        int64(2): "land_lahn_leun",
        int64(3): "land_lahn_kalk",
        int64(4): "land_dill_assl",
        int64(5): "land_lahn_rest",
    }


def test_missing_file(tmp_path: str) -> None:
    with pytest.raises(FileNotFoundError) as info:
        reading.read_mapping_table(dirpath=tmp_path)
    assert str(info.value) == (
        f"Geopackage `{os.path.join(tmp_path, FILENAME_FEATURE)}` does not exist."
    )


def test_missing_table(fixture_project: None) -> None:
    gpkg = geopkg.GeoPackage(DIRPATH_FEATURE)
    gpkg.tables[constants.MAPPING_TABLE].drop()
    gpkg.connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        f"Geopackage `{DIRPATH_FEATURE}` does not contain the required mapping table "
        f"`element_id2name`."
    )


def test_missing_column(fixture_project: None) -> None:
    modify_table().connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        f"Geopackage `{DIRPATH_FEATURE}` does not contain a column named `element_id`."
    )


def test_missing_id(fixture_project: None) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="INTEGER"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="TEXT", size=100),
    )
    with gpkg.connection as connection:
        for id_, name in ((1, '"one"'), ("NULL", '"two"'), (3, '"three"')):
            _ = connection.execute(
                f"INSERT INTO {constants.MAPPING_TABLE}"
                f"({constants.ELEMENT_ID}, {constants.ELEMENT_NAME}) "
                f"VALUES ({id_}, {name})"
            )
    gpkg.connection.close()
    with pytest.warns(
        UserWarning,
        match=re.escape(
            "Column `element_id` of table `element_id2name` of geopackage "
            f"`{DIRPATH_FEATURE}` contains at least one missing value."
        ),
    ):
        table = reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert table == {int64(1): "one", int64(3): "three"}


def test_missing_name(fixture_project: None) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="INTEGER"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="TEXT", size=100),
    )
    with gpkg.connection as connection:
        for id_, name in ((1, '"one"'), (2, "NULL"), (3, '"three"')):
            _ = connection.execute(
                f"INSERT INTO {constants.MAPPING_TABLE}"
                f"({constants.ELEMENT_ID}, {constants.ELEMENT_NAME}) "
                f"VALUES ({id_}, {name})"
            )
    gpkg.connection.close()
    with pytest.warns(
        UserWarning,
        match=re.escape(
            "Column `element_name` of table `element_id2name` of geopackage "
            f"`{DIRPATH_FEATURE}` contains at least one missing value."
        ),
    ):
        table = reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert table == {int64(1): "one", int64(3): "three"}


def test_wrong_id_type(fixture_project: None) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="DOUBLE"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="TEXT", size=100),
    )
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {constants.MAPPING_TABLE}"
            f"({constants.ELEMENT_ID}, {constants.ELEMENT_NAME}) VALUES (1.5, 'test')"
        )
    gpkg.connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        "Column `element_id` of table `element_id2name` of geopackage "
        f"`{DIRPATH_FEATURE}` contains non-integer values."
    )


def test_wrong_name_type(fixture_project: None) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="INTEGER"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="DOUBLE"),
    )
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {constants.MAPPING_TABLE}"
            f"({constants.ELEMENT_ID}, {constants.ELEMENT_NAME}) VALUES (1, 1.5)"
        )
    gpkg.connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=DIRPATH_MPR_DATA)
    assert str(info.value) == (
        "Column `element_name` of table `element_id2name` of geopackage "
        f"`{DIRPATH_FEATURE}` contains non-string values."
    )
