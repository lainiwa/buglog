"""Nox sessions."""
import os
import tempfile
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, ContextManager, Iterator
import subprocess

import nox
from nox.sessions import Session


package = "buglog"

nox.options.sessions = (
    # Extra:: fmt
    "reorder_imports",
    "autoflake",
    "pyupgrade",
    "black",
    # Security
    "safety",
    # Type checking
    "mypy",
    # Extra:: lint
    "lint",
    # Extra:: test
    "tests",
    # "coverage",
    # "pytype",
)

locations = (
    "src/",
    "tests/",
    "noxfile.py",
    "docs/conf.py",
)


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
    colon_dirs = ":".join(filter(os.path.isdir, locations))
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "reorder-python-imports")
        session.run(
            "reorder-python-imports",
            "--py37-plus",
            "--unclassifiable-application-module=buglog",
            f"--application-directories={colon_dirs}",
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
    args = session.posargs or locations
    with constraints_file("--without-hashes", "-E", "lint") as reqs_path:
        session.install("-r", f"{reqs_path}")
        session.run("flakehell", "lint", *args)
        session.run(
            "yamllint",
            "--format",
            "parsable",
            "--strict",
            ".github/",
            ".readthedocs.yml",
        )
        session.run(
            "dead", "--exclude", "(data/config.py$|^docs|^noxfile.py$)"
        )
        # poetry run vulture src tests --exclude 'data/config.py'


# @nox.session(python=["3.8", "3.7"])
@nox.session(python="3.8")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    with all_constraints_file() as reqs_path:
        session.install(f"--constraint={reqs_path}", "mypy", "pydantic")
        session.run("mypy", *args)


# @nox.session(python=["3.8", "3.7"])
@nox.session(python=["3.8"])
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    with constraints_file("--without-hashes", "-E", "test") as reqs_path:
        session.install(".")
        session.install("-r", f"{reqs_path}")
        session.install("nox")
        session.run("pytest", *args)


@nox.session(python="3.8")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    with constraints_file("--without-hashes", "-E", "test") as reqs_path:
        session.install("-r", f"{reqs_path}")
        session.run("coverage", "xml", "--fail-under=0")
        session.run("codecov", *session.posargs)


@nox.session(python="3.8")
def docs(session: Session) -> None:
    """Build the documentation."""
    with constraints_file("--without-hashes", "-E", "docs") as reqs_path:
        session.install("-r", f"{reqs_path}")
        session.install(".")
        session.run("sphinx-build", "docs", "docs/_build")
