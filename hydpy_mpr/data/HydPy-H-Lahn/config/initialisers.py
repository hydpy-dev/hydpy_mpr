import os

import hydpy
from hydpy import pub


def initialise_lahn() -> hydpy.HydPy:
    hp = hydpy.HydPy("HydPy-H-Lahn")
    pub.timegrids = "1996-01-01", "1998-01-01", "1d"
    hp.prepare_everything()
    return hp
