"""Nox sessions."""
import itertools
import os
import tempfile
from contextlib import contextmanager
from functools import lru_cache
from glob import glob
from typing import Any, ContextManager, Iterator
import subprocess

import nox
from nox.sessions import Session


package = "buglog"

nox.options.sessions = (
    # extra: fmt
    "reorder_imports",
    "autoflake",
    "pyupgrade",
    "black",
    # Security
    "safety",
    # Type checking
    "mypy",
    # extra: lint
    "lint",
    # extra: test
    "tests",
    # "coverage",
    # "pytype",
)

locations = (
    "src",
    "tests",
    "noxfile.py",
    "docs/conf.py",
)

py_files = [
    os.path.abspath(file)
    for file in itertools.chain.from_iterable(
        glob(f"{loc}/**/*.py", recursive=True) if os.path.isdir(loc) else [loc]
        for loc in locations
    )
]


@lru_cache()
def constraints(*args: str, **kwargs: Any) -> str:
    return subprocess.check_output(
        [
            "poetry",
            "export",
            "--format=requirements.txt",
            *args,
        ],
        **kwargs,
    ).decode("utf-8")


@contextmanager
def constraints_file(*args: str, **kwargs: Any) -> Iterator[str]:
    try:
        reqs_file = tempfile.NamedTemporaryFile()
        with open(reqs_file.name, "w") as fout:
            fout.write(constraints(*args, **kwargs))
        yield reqs_file.name
    finally:
        reqs_file.close()


def all_constraints_file(*args: str, **kwargs: Any) -> ContextManager[str]:
    return constraints_file(
        "--dev",
        "-E",
        "lint",
        "-E",
        "fmt",
        "-E",
        "test",
        "-E",
        "docs",
        *args,
        **kwargs,
    )


@nox.session(python="3.8")
def reorder_imports(session: Session) -> None:
    """Reformat imports."""
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "reorder-python-imports")
        # session.cd("src/buglog")
        session.run(
            "reorder-python-imports",
            "--py37-plus",
            "--unclassifiable-application-module=buglog",
            "--application-directories=src:tests",
            # *glob("**/*.py", recursive=True),
            success_codes=[0, 1],
        )


@nox.session(python="3.8")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "black")
        session.run("black", *args)


@nox.session(python="3.8")
def docformatter(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "docformatter")
        session.run("docformatter", *args)


@nox.session(python="3.8")
def autoflake(session: Session) -> None:
    """Upgrade syntax to newer versions."""
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "autoflake")
        session.run(
            "autoflake",
            "--in-place",
            "--remove-all-unused-imports",
            "--remove-unused-variable",
            "--recursive",
            ".",
        )


@nox.session(python="3.8")
def pyupgrade(session: Session) -> None:
    """Upgrade syntax to newer versions."""
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "pyupgrade")
        session.run("pyupgrade", "--py37-plus")


@nox.session(python="3.8")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    with all_constraints_file("--without-hashes") as reqs_path:
        session.install(f"--constraint={reqs_path}", "safety")
        session.run("safety", "check", f"--file={reqs_path}", "--full-report")


# @nox.session(python=["3.8", "3.7"])
@nox.session(python="3.8")
def lint(session: Session) -> None:
    """Lint using flake8."""
    session.posargs or locations
    with constraints_file("--without-hashes", "-E", "lint") as reqs_path:
        session.install("-r", f"{reqs_path}")
        session.run("flakehell", "lint", "src", "tests")
        # session.run("flake8", "src")
        # session.run("flake8", *args)


# @nox.session(python=["3.8", "3.7"])
@nox.session(python="3.8")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "mypy", "pydantic")
        session.run("mypy", *args)


# @nox.session(python="3.7")
# def pytype(session: Session) -> None:
#     """Type-check using pytype."""
#     args = session.posargs or ["--disable=import-error", *locations]
#     install_with_constraints(session, "pytype")
#     session.run("pytype", *args)


# @nox.session(python=["3.8", "3.7"])
@nox.session(python=["3.8"])
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    with constraints_file("--without-hashes", "-E", "test") as reqs_path:
        session.install(".")
        session.install("-r", f"{reqs_path}")
        session.install("nox")
        # session.install(f"--constraint={reqs_path}", "mypy", "pydantic")
        # session.run("flake8", "src")
        session.run("pytest", *args)


@nox.session(python="3.8")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    with constraints_file("--without-hashes", "-E", "test") as reqs_path:
        session.install("-r", f"{reqs_path}")
        session.run("coverage", "xml", "--fail-under=0")
        session.run("codecov", *session.posargs)


# @nox.session(python=["3.8", "3.7"])
# def typeguard(session: Session) -> None:
#     """Runtime type checking using Typeguard."""
#     args = session.posargs or ["-m", "not e2e"]
#     session.run("poetry", "install", "--no-dev", external=True)
#     install_with_constraints(session, "pytest", "pytest-mock", "typeguard")
#     session.run("pytest", f"--typeguard-packages={package}", *args)


# @nox.session(python=["3.8", "3.7"])
# def xdoctest(session: Session) -> None:
#     """Run examples with xdoctest."""
#     args = session.posargs or ["all"]
#     session.run("poetry", "install", "--no-dev", external=True)
#     install_with_constraints(session, "xdoctest")
#     session.run("python", "-m", "xdoctest", package, *args)


@nox.session(python="3.8")
def docs(session: Session) -> None:
    """Build the documentation."""
    with constraints_file("--without-hashes", "-E", "docs") as reqs_path:
        session.install("-r", f"{reqs_path}")
        session.install(".")
        session.run("sphinx-build", "docs", "docs/_build")
