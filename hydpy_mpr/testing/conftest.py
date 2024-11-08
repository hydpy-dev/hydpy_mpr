# pylint: disable=missing-docstring, redefined-outer-name

from __future__ import annotations

import os

from hydpy import pub
import pytest

from hydpy_mpr.source import constants
from hydpy_mpr.source.typing_ import *
from hydpy_mpr import testing


@pytest.fixture
def dirpath_project() -> str:
    return "HydPy-H-Lahn"


@pytest.fixture
def dirpath_mpr_data(dirpath_project: str) -> str:
    return os.path.join(dirpath_project, "mpr_data")


@pytest.fixture
def filepath_feature(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, constants.FEATURE_GPKG)


@pytest.fixture
def dirpath_config(dirpath_mpr_data: str) -> str:
    return os.path.join(dirpath_mpr_data, "config")


@pytest.fixture
def dirpath_experiment1(dirpath_config: str) -> str:
    return os.path.join(dirpath_config, "experiment_1.py")


@pytest.fixture
def arrange_project() -> Iterator[None]:
    with pub.options.printprogress(False):
        reset_workingdir = testing.prepare_project("HydPy-H-Lahn")
        yield
        reset_workingdir()
