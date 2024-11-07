"""This module defines different "sessions"; each session tests certain aspects of
HydPy-MPR, some in a freshly set up virtual environment.

To execute all sessions, install `Nox`, open a command-line prompt, navigate to the
directory containing this nox file and write "nox".  To run specific sessions, write,
for example:

nox -s doctest -s pylint
"""

import contextlib
import os
import shutil
from typing import *
from typing_extensions import assert_never

import nox


def _install_hydpy_mpr(session: nox.Session) -> None:
    wheels = [
        os.path.join("dist", fn) for fn in os.listdir("dist") if fn.endswith(".whl")
    ]
    if wheels:
        print("available wheels:")
        for wheel in wheels:
            print(f"\t{wheel}")
    else:
        raise FileNotFoundError("no wheel available")
    if len(wheels) == 1:
        wheel = wheels[0]
        print(f"installing wheel {wheel}")
        session.install(wheel)
    else:
        print("let pip determine the appropriate wheel")
        session.install("hydpy_mpr", "--find-links", "dist")


@nox.session
def pytest(session: nox.Session) -> None:
    """Execute all unit and integration tests and measure code coverage."""
    _install_hydpy_mpr(session)
    session.run("pytest", "--cov", "--cov-report", "term-missing")


@nox.session
def doctest(session: nox.Session) -> None:
    """Execute script `run_doctests.py`."""
    _install_hydpy_mpr(session)
    session.run("python", "hydpy_mpr/testing/run_doctests.py", *session.posargs)


@nox.session(python=False)
def black(session: nox.Session) -> None:
    """Use `black` to check the source formatting."""
    session.run("black", "hydpy_mpr", "--check")


@nox.session(python=False)
def pylint(session: nox.Session) -> None:
    """Use `pylint` to evaluate the code style."""
    session.run("pylint", "hydpy_mpr")


@nox.session(python=False)
def mypy(session: nox.Session) -> None:
    """Use "mypy" to check the correctness of all type hints and the source code's type
    safety strictly."""
    session.run("mypy", "hydpy_mpr")
