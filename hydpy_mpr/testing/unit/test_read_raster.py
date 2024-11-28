# pylint: disable=missing-docstring, unused-argument, too-many-arguments, too-many-positional-arguments

from __future__ import annotations
import copy
import dataclasses
import os
import re
import shutil

import numpy
import pytest

import hydpy_mpr
from hydpy_mpr.source import constants
from hydpy_mpr.source.typing_ import *


def test_read_geotiff_int_okay(
    arrange_project: None, filepath_element_id_15km: str
) -> None:
    raster = hydpy_mpr.read_geotiff(filepath=filepath_element_id_15km, integer=True)
    assert raster.shape == (10, 10)
    assert raster.missingvalue == -9999
    values = raster.values
    assert numpy.sum(~raster.mask) == numpy.sum(values == -9999) == 73
    assert tuple(numpy.sum(values == id_) for id_ in range(6)) == (0, 7, 5, 9, 3, 3)


def test_read_geotiff_int_but_dtype_is_float(
    arrange_project: None, filepath_sand_2m_15km: str
) -> None:
    with pytest.warns(
        UserWarning,
        match=re.escape(
            f"The data type of tiff file `{filepath_sand_2m_15km}` is `float32` but "
            f"integer values are expected."
        ),
    ):
        raster = hydpy_mpr.read_geotiff(filepath=filepath_sand_2m_15km, integer=True)
        assert isinstance(raster, hydpy_mpr.RasterInt)


def test_read_geotiff_float_okay(
    arrange_project: None, filepath_sand_2m_15km: str
) -> None:
    raster = hydpy_mpr.read_geotiff(filepath=filepath_sand_2m_15km)
    assert raster.shape == (10, 10)
    assert numpy.nanmin(raster.values) == pytest.approx(15.359077453613281)
    assert numpy.nanmax(raster.values) == pytest.approx(24.92906379699707)
    assert numpy.sum(numpy.isnan(raster.values)) == 76
    assert numpy.sum(~raster.mask) == 76


def test_read_raster_missing_file(filepath_element_id_15km: str) -> None:
    with pytest.raises(FileNotFoundError) as info:
        hydpy_mpr.read_geotiff(filepath=filepath_element_id_15km, integer=True)
    assert str(info.value) == (f"GeoTiff `{filepath_element_id_15km}` does not exist.")


def test_raster_equality(arrange_project: None, filepath_element_id_15km: str) -> None:
    raster1 = hydpy_mpr.read_geotiff(filepath=filepath_element_id_15km, integer=True)
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
    @dataclasses.dataclass(kw_only=True)
    class MyRaster1(hydpy_mpr.RasterInt):
        pass

    raster2.__class__ = MyRaster1
    assert raster1 == raster2

    # incompatible subclass:
    @dataclasses.dataclass(kw_only=True)
    class MyRaster2(hydpy_mpr.RasterInt):
        test: int = dataclasses.field(init=False)

    raster2.__class__ = MyRaster2
    assert raster1 != raster2


def test_read_rastergroup_okay(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    dirname_raster_15km: NameRasterGroup,
    filepath_element_id_15km: str,
    filepath_subunit_id_15km: str,
    filename_sand_2m_15km: str,
    filepath_sand_2m_15km: str,
    rastername_sand_2m_15km: NameRaster,
) -> None:
    group = hydpy_mpr.RasterGroup(
        mprpath=dirpath_mpr_data,
        name=dirname_raster_15km,
        raster_names=(rastername_sand_2m_15km,),
    )
    assert group.element_raster == hydpy_mpr.read_geotiff(
        filepath=filepath_element_id_15km, integer=True
    )
    assert group.subunit_raster == hydpy_mpr.read_geotiff(
        filepath=filepath_subunit_id_15km, integer=True
    )
    assert group.data_rasters[
        hydpy_mpr.RasterGroup.filename2rastername(filename_sand_2m_15km)
    ] == hydpy_mpr.read_geotiff(filepath=filepath_sand_2m_15km)


def test_read_rastergroup_missing_dirpath(
    dirpath_mpr_data: DirpathMPRData,
    dirname_raster_15km: NameRasterGroup,
    dirpath_raster_15km: str,
) -> None:
    with pytest.raises(FileNotFoundError) as info:
        hydpy_mpr.RasterGroup(
            mprpath=dirpath_mpr_data, name=dirname_raster_15km, raster_names=()
        )
    assert str(info.value) == (
        f"The requested raster group directory `{dirpath_raster_15km}` does not exist."
    )


def test_read_rastergroup_missing_element_id_file(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    dirname_raster_15km: NameRasterGroup,
    dirpath_raster_15km: str,
    filepath_element_id_15km: str,
) -> None:
    os.remove(filepath_element_id_15km)
    with pytest.raises(FileNotFoundError) as info:
        hydpy_mpr.RasterGroup(
            mprpath=dirpath_mpr_data, name=dirname_raster_15km, raster_names=()
        )
    assert str(info.value) == (
        f"The raster group directory `{dirpath_raster_15km}` does not contain an "
        f"`{constants.ELEMENT_ID}` raster file."
    )


def test_read_rastergroup_missing_subunit_id_file(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    dirname_raster_15km: NameRasterGroup,
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
        hydpy_mpr.RasterGroup(
            mprpath=dirpath_mpr_data, name=dirname_raster_15km, raster_names=()
        )


def test_read_rastergroup_inconsistent_shape(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    dirname_raster_15km: NameRasterGroup,
    filepath_element_id_5km: str,
    filepath_element_id_15km: str,
) -> None:
    shutil.copy(filepath_element_id_5km, filepath_element_id_15km)
    with pytest.raises(TypeError) as info:
        hydpy_mpr.RasterGroup(
            mprpath=dirpath_mpr_data, name=dirname_raster_15km, raster_names=()
        )
    assert str(info.value) == (
        f"Raster group `{dirname_raster_15km}` is inconsistent: shape `(28, 29)` of "
        f"raster `{constants.ELEMENT_ID}` conflicts with shape `(10, 10)` of raster "
        f"`{constants.SUBUNIT_ID}`."
    )


def test_read_rastergroups_okay(
    arrange_project: None,
    dirpath_mpr_data: DirpathMPRData,
    dirname_raster_15km: NameRasterGroup,
    regionaliser_fc_2m: hydpy_mpr.RasterRegionaliser,
    rastername_clay_2m_15km: NameRaster,
    rastername_density_2m_15km: NameRaster,
) -> None:
    groups = hydpy_mpr.RasterGroups(
        mprpath=dirpath_mpr_data, equations=(regionaliser_fc_2m,)
    )
    group = hydpy_mpr.RasterGroup(
        mprpath=dirpath_mpr_data,
        name=dirname_raster_15km,
        raster_names=(rastername_density_2m_15km, rastername_clay_2m_15km),
    )
    assert groups[dirname_raster_15km] == group


def test_read_rastergroups_rastergroup_missing() -> None:
    groups = hydpy_mpr.RasterGroups(mprpath=DirpathMPRData("test"), equations=())
    with pytest.raises(KeyError) as info:
        groups[NameRasterGroup("wrong")]  # pylint: disable=expression-not-assigned
    assert str(info.value) == "'No raster group named `wrong` available.'"
