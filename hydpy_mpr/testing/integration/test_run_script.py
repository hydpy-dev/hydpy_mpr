import os
import runpy
import sys

def test_example_1(fixture_project: None) -> None:
    sys.path.insert(0, os.path.join("HydPy-H-Lahn", "mpr_data", "config"))
    runpy.run_path(
        os.path.join("HydPy-H-Lahn", "mpr_data", "config", "experiment_1.py")
    )
