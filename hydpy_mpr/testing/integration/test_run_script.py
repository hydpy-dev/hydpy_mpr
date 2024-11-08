# pylint: disable=missing-docstring, unused-argument

import os
import runpy
import sys

import pytest


@pytest.mark.integration_test
def test_example_1(
    arrange_project: None,
    dirpath_project: str,
    dirpath_config: str,
    dirpath_experiment1: str,
) -> None:
    sys.path.insert(0, dirpath_config)
    runpy.run_path(dirpath_experiment1, run_name="__main__")
    result = runpy.run_path(
        os.path.join(dirpath_project, "control", "experiment_1", "land_dill_assl.py")
    )
    fc_values = result["fc"].values
    assert min(fc_values) == max(fc_values) == pytest.approx(278.73223239535025)
