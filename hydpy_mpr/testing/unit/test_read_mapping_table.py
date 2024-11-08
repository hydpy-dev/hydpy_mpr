# pylint: disable=missing-docstring, unused-argument

from __future__ import annotations
import os
import re

from fudgeo import geopkg
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import reading
from hydpy_mpr.source.typing_ import *


def modify_table(*fields: geopkg.Field, filepath: str) -> geopkg.GeoPackage:
    gpkg = geopkg.GeoPackage(filepath)
    gpkg.create_table(constants.MAPPING_TABLE, fields=fields, overwrite=True)
    return gpkg


def test_everything_okay(arrange_project: None, dirpath_mpr_data: str) -> None:
    assert reading.read_mapping_table(dirpath=dirpath_mpr_data) == {
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
        f"Geopackage `{os.path.join(tmp_path, constants.FEATURE_GPKG)}` does not exist."
    )


def test_missing_table(
    arrange_project: None, filepath_feature: str, dirpath_mpr_data: str
) -> None:
    gpkg = geopkg.GeoPackage(filepath_feature)
    gpkg.tables[constants.MAPPING_TABLE].drop()
    gpkg.connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=dirpath_mpr_data)
    assert str(info.value) == (
        f"Geopackage `{filepath_feature}` does not contain the required mapping table "
        f"`element_id2name`."
    )


def test_missing_column(
    arrange_project: None, dirpath_mpr_data: str, filepath_feature: str
) -> None:
    modify_table(filepath=filepath_feature).connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=dirpath_mpr_data)
    assert str(info.value) == (
        f"Geopackage `{filepath_feature}` does not contain a column named `element_id`."
    )


def test_missing_id(
    arrange_project: None, dirpath_mpr_data: str, filepath_feature: str
) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="INTEGER"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="TEXT", size=100),
        filepath=filepath_feature,
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
            f"`{filepath_feature}` contains at least one missing value."
        ),
    ):
        table = reading.read_mapping_table(dirpath=dirpath_mpr_data)
    assert table == {int64(1): "one", int64(3): "three"}


def test_missing_name(
    arrange_project: None, dirpath_mpr_data: str, filepath_feature: str
) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="INTEGER"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="TEXT", size=100),
        filepath=filepath_feature,
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
            f"`{filepath_feature}` contains at least one missing value."
        ),
    ):
        table = reading.read_mapping_table(dirpath=dirpath_mpr_data)
    assert table == {int64(1): "one", int64(3): "three"}


def test_wrong_id_type(
    arrange_project: None, dirpath_mpr_data: str, filepath_feature: str
) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="DOUBLE"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="TEXT", size=100),
        filepath=filepath_feature,
    )
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {constants.MAPPING_TABLE}"
            f"({constants.ELEMENT_ID}, {constants.ELEMENT_NAME}) VALUES (1.5, 'test')"
        )
    gpkg.connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=dirpath_mpr_data)
    assert str(info.value) == (
        "Column `element_id` of table `element_id2name` of geopackage "
        f"`{filepath_feature}` contains non-integer values."
    )


def test_wrong_name_type(
    arrange_project: None, dirpath_mpr_data: str, filepath_feature: str
) -> None:
    gpkg = modify_table(
        geopkg.Field(name=constants.ELEMENT_ID, data_type="INTEGER"),
        geopkg.Field(name=constants.ELEMENT_NAME, data_type="DOUBLE"),
        filepath=filepath_feature,
    )
    with gpkg.connection as connection:
        connection.execute(
            f"INSERT INTO {constants.MAPPING_TABLE}"
            f"({constants.ELEMENT_ID}, {constants.ELEMENT_NAME}) VALUES (1, 1.5)"
        )
    gpkg.connection.close()
    with pytest.raises(TypeError) as info:
        reading.read_mapping_table(dirpath=dirpath_mpr_data)
    assert str(info.value) == (
        "Column `element_name` of table `element_id2name` of geopackage "
        f"`{filepath_feature}` contains non-string values."
    )
