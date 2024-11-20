# pylint: disable=missing-docstring, unused-argument

import os
import runpy
import sys

import numpy
import pytest


@pytest.mark.integration_test
def test_example_1(
    arrange_project: None,
    dirpath_project: str,
    dirpath_config: str,
    filepath_experiment_subunit_level: str,
) -> None:
    sys.path.insert(0, dirpath_config)
    runpy.run_path(filepath_experiment_subunit_level, run_name="__main__")
    result = runpy.run_path(
        os.path.join(dirpath_project, "control", "calibrated", "land_dill_assl.py")
    )
    fc = result["fc"].values
    assert numpy.min(fc[:4]) == numpy.max(fc[:4]) == pytest.approx(278.0)
    assert fc[4:-6] == pytest.approx([280.47638276, 264.40416301])
    assert numpy.min(fc[-6:]) == numpy.max(fc[-6:]) == pytest.approx(278.0)
