# pylint: disable=missing-docstring, unused-argument, too-many-arguments, too-many-positional-arguments

from __future__ import annotations
import copy
import dataclasses
import os
import re
import shutil

import numpy
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source import reading


def test_read_geotiff_int_okay(
    arrange_project: None, filepath_element_id_15km: str
) -> None:
    raster = reading.read_geotiff(filepath_element_id_15km, datatype="int")
    assert raster.shape == (10, 10)
    assert raster.missingvalue == -9999
    values = raster.values
    assert numpy.sum(~raster.mask) == numpy.sum(values == -9999) == 73
    assert tuple(numpy.sum(values == id_) for id_ in range(6)) == (0, 7, 5, 9, 3, 3)


def test_read_geotiff_float_okay(
    arrange_project: None, filepath_element_sand: str
) -> None:
    raster = reading.read_geotiff(filepath_element_sand, datatype="float")
    assert raster.shape == (10, 10)
    assert numpy.nanmin(raster.values) == pytest.approx(15.359077453613281)
    assert numpy.nanmax(raster.values) == pytest.approx(24.92906379699707)
    assert numpy.sum(numpy.isnan(raster.values)) == 76
    assert numpy.sum(~raster.mask) == 76


def test_read_raster_missing_file(filepath_element_id_15km: str) -> None:
    with pytest.raises(FileNotFoundError) as info:
        reading.read_geotiff(filepath_element_id_15km, datatype="int")
    assert str(info.value) == (f"GeoTiff `{filepath_element_id_15km}` does not exist.")


def test_raster_equality(arrange_project: None, filepath_element_id_15km: str) -> None:
    raster1 = reading.read_geotiff(filepath_element_id_15km, datatype="int")
    raster2 = copy.deepcopy(raster1)

    # everything equal:
    assert raster1 == raster2

    # normal attribute differs:
    raster2.shape = (1, 3)
    assert raster1 != raster2
    raster2.shape = raster1.shape

    # array attribute differs:
    raster2.values[0, 0] = 1.0
    assert raster1 != raster2
    raster2.values[0, 0] = raster1.values[0, 0]
    raster2.mask[0, 0] = True
    assert raster1 != raster2
    raster2.mask[0, 0] = raster1.mask[0, 0]

    # different types:
    assert raster1 != 1

    # compatible subclass:
    @dataclasses.dataclass
    class MyRaster1(reading.RasterInt):
        pass

    raster2.__class__ = MyRaster1
    assert raster1 == raster2

    # incompatible subclass:
    @dataclasses.dataclass
    class MyRaster2(reading.RasterInt):
        test: int = dataclasses.field(init=False)

    raster2.__class__ = MyRaster2
    assert raster1 != raster2


def test_read_rastergroup_okay(
    arrange_project: None,
    dirpath_mpr_data: str,
    dirname_raster_15km: str,
    filepath_element_id_15km: str,
    filepath_subunit_id_15km: str,
    filename_element_sand_15km: str,
    filepath_element_sand: str,
) -> None:
    group = reading.RasterGroup(mprpath=dirpath_mpr_data, name=dirname_raster_15km)
    assert group.element_raster == reading.read_geotiff(
        filepath_element_id_15km, datatype="int"
    )
    assert group.subunit_raster == reading.read_geotiff(
        filepath_subunit_id_15km, datatype="int"
    )
    assert group.data_rasters[
        filename_element_sand_15km.split(".")[0]
    ] == reading.read_geotiff(filepath_element_sand, datatype="float")


def test_read_rastergroup_missing_dirpath(
    dirpath_mpr_data: str, dirname_raster_15km: str, dirpath_raster_15km: str
) -> None:
    with pytest.raises(FileNotFoundError) as info:
        reading.RasterGroup(mprpath=dirpath_mpr_data, name=dirname_raster_15km)
    assert str(info.value) == (
        f"The requested raster group directory `{dirpath_raster_15km}` does not exist."
    )


def test_read_rastergroup_missing_element_id_file(
    arrange_project: None,
    dirpath_mpr_data: str,
    dirname_raster_15km: str,
    dirpath_raster_15km: str,
    filepath_element_id_15km: str,
) -> None:
    os.remove(filepath_element_id_15km)
    with pytest.raises(FileNotFoundError) as info:
        reading.RasterGroup(mprpath=dirpath_mpr_data, name=dirname_raster_15km)
    assert str(info.value) == (
        f"The raster group directory `{dirpath_raster_15km}` does not contain an "
        f"`{constants.ELEMENT_ID}` raster file."
    )


def test_read_rastergroup_missing_subunit_id_file(
    arrange_project: None,
    dirpath_mpr_data: str,
    dirname_raster_15km: str,
    dirpath_raster_15km: str,
    filepath_subunit_id_15km: str,
) -> None:
    os.remove(filepath_subunit_id_15km)
    with pytest.warns(
        UserWarning,
        match=re.escape(
            f"The raster group directory `{dirpath_raster_15km}` does not contain a "
            f"`{constants.SUBUNIT_ID}` raster file."
        ),
    ):
        reading.RasterGroup(mprpath=dirpath_mpr_data, name=dirname_raster_15km)


def test_read_rastergroup_inconsistent_shape(
    arrange_project: None,
    dirpath_mpr_data: str,
    dirname_raster_15km: str,
    filepath_element_id_5km: str,
    filepath_element_id_15km: str,
) -> None:
    shutil.copy(filepath_element_id_5km, filepath_element_id_15km)
    with pytest.raises(TypeError) as info:
        reading.RasterGroup(mprpath=dirpath_mpr_data, name=dirname_raster_15km)
    assert str(info.value) == (
        f"Raster group `{dirname_raster_15km}` is inconsistent: shape `(28, 29)` of "
        f"raster `{constants.ELEMENT_ID}` conflicts with shape `(10, 10)` of raster "
        f"`{constants.SUBUNIT_ID}.tif`."
    )


def test_read_rastergroups_okay(
    arrange_project: None, dirpath_mpr_data: str, dirname_raster_15km: str
) -> None:
    groups = reading.RasterGroups(mprpath=dirpath_mpr_data)
    group = reading.RasterGroup(mprpath=dirpath_mpr_data, name=dirname_raster_15km)
    assert groups[dirname_raster_15km] == group
