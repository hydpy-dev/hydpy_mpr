# pylint: disable=missing-docstring, unused-argument

import os
import runpy
import sys

import pytest


@pytest.mark.integration_test
def test_example_1(fixture_project: None) -> None:
    sys.path.insert(0, os.path.join("HydPy-H-Lahn", "mpr_data", "config"))
    runpy.run_path(
        os.path.join("HydPy-H-Lahn", "mpr_data", "config", "experiment_1.py"),
        run_name="__main__",
    )

    result = runpy.run_path(
        os.path.join("HydPy-H-Lahn", "control", "experiment_1", "land_dill_assl.py")
    )
    fc_values = result["fc"].values
    assert min(fc_values) == max(fc_values) == pytest.approx(278.73223239535025)
