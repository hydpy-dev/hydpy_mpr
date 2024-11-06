# pylint: disable=missing-docstring

from __future__ import annotations

from hydpy import pub
import pytest

from hydpy_mpr.source.typing_ import *
from hydpy_mpr import testing


@pytest.fixture
def fixture_project() -> Iterator[None]:
    with pub.options.printprogress(False):
        reset_workingdir = testing.prepare_project("HydPy-H-Lahn")
        yield
        reset_workingdir()
