# pylint: disable=missing-docstring

from pytest import fixture

from hydpy_mpr.source.typing_ import Iterator
from hydpy_mpr.testing import prepare_project


@fixture
def fixture_project() -> Iterator[None]:
    reset_workingdir = prepare_project("HydPy-H-Lahn")
    yield
    reset_workingdir()
