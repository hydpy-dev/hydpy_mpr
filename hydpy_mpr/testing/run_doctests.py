"""Evaluate all doctests defined in the library's Python, Cython, and Markdown files."""

from __future__ import annotations
import doctest
import importlib
import os
import sys
import unittest
from typing import NoReturn, TypeAlias

import click

# import hydpy_mpr  import below


Results: TypeAlias = dict[str, tuple[unittest.TestResult, int]]


@click.command()
@click.option(
    "-p",
    "--path",
    type=str,
    required=False,
    default=None,
    help="Path to the tested HydPy-MPR package.",
)
@click.option(
    "-f",
    "--files",
    type=str,
    required=False,
    multiple=True,
    default=(),
    help="Names of the analysed files.",
)
def main(path: str | None, files: list[str]) -> NoReturn:
    """Search for and analyse files that contain doctests."""

    _filter_filenames = _FilterFilenames(files)
    if path is not None:
        sys.path.insert(0, path)

    import hydpy_mpr  # pylint: disable=import-outside-toplevel

    os.chdir(hydpy_mpr.__path__[0])

    successfull_tests: Results = {}
    failed_tests: Results = {}
    for dirname in ("examples", "source", "testing"):
        dirpath = os.path.abspath(dirname)
        for filename in sorted(_filter_filenames(os.listdir(dirpath))):
            _analyse_file(
                filepath=os.path.join(dirpath, filename),
                failed_tests=failed_tests,
                successfull_tests=successfull_tests,
            )

    _summarise_results(failed_tests=failed_tests, successfull_tests=successfull_tests)

    raise SystemExit(min(len(failed_tests), 1))


def _print(*args: str) -> None:
    print(*args)
    sys.stdout.flush()


class _FilterFilenames:
    _files_doctests: set[str] | None

    def __init__(self, files_doctests: list[str] | None, /) -> None:
        self._files_doctests = set(files_doctests) if files_doctests else None

    def __call__(self, filenames: list[str], /) -> list[str]:
        if self._files_doctests is not None:
            filenames = [fn for fn in filenames if fn in self._files_doctests]
        return [fn for fn in filenames if fn.rsplit(".")[-1] in ("py", "pyx", "md")]


def _analyse_file(
    *, filepath: str, failed_tests: Results, successfull_tests: Results
) -> None:
    """Analyse a single Python, Cython, or Markdown file."""

    # Make a test suite for the given file:
    suite = unittest.TestSuite()
    if filepath.endswith(".py"):
        modulename = filepath.split("hydpy_mpr")[-1].replace(os.sep, ".")
        modulename = f"hydpy_mpr{modulename[:-3]}"
        test = doctest.DocTestSuite(importlib.import_module(modulename))
    else:
        test = doctest.DocFileSuite(filepath, module_relative=False)
    suite.addTest(test)

    # Run the tests:
    with open(os.devnull, "w", encoding="utf-8") as void:
        runner = unittest.TextTestRunner(stream=void)
        result = runner.run(suite)

    # Store the test results:
    nmbproblems = len(result.errors) + len(result.failures)
    if nmbproblems:
        failed_tests[filepath] = (result, nmbproblems)
    else:
        successfull_tests[filepath] = (result, nmbproblems)

    # Report all errors directly:
    if problems := result.errors + result.failures:
        _print(f"\nDetailed error information on file {filepath}:")
        for idx, problem in enumerate(problems):
            _print(f"    Error no. {idx + 1}:")
            _print(f"        {problem[0]}")
            for line in problem[1].split("\n"):
                _print(f"        {line}")


def _summarise_results(*, failed_tests: Results, successfull_tests: Results) -> None:
    """Print a summary of the test results."""

    if successfull_tests:
        _print("\nIn the following files, no doctest failed:")
        for name, (result, _) in sorted(successfull_tests.items()):
            if name.endswith(".py"):
                _print(f"    {name} ({result.testsRun} successes)")
            else:
                _print(f"    {name}")

    if failed_tests:
        _print("\nIn the following files, at least one doctest failed:")
        for name, (result, nmbproblems) in sorted(failed_tests.items()):
            if name.endswith(".py"):
                _print(f"    {name} ({nmbproblems} failures/errors)")
            else:
                _print(f"    {name}")
        _print("")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
