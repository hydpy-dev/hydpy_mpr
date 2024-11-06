# pylint: disable=missing-docstring

from __future__ import annotations
from hydpy import pub
from pytest import fixture

from hydpy_mpr.source.typing_ import Iterator
from hydpy_mpr.testing import prepare_project


@fixture
def fixture_project() -> Iterator[None]:
    with pub.options.printprogress(False):
        reset_workingdir = prepare_project("HydPy-H-Lahn")
        yield
        reset_workingdir()
