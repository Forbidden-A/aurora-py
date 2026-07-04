import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = [
    "lint",
    "typecheck",
]  # "test"]


@nox.session(python="3.14")
def lint(session: nox.Session) -> None:
    """Run ruff linter and formatter checks."""
    session.install("-e", ".")
    session.install("ruff")

    session.run("ruff", "check", "src/")
    # session.run("ruff", "check", "tests/")

    session.run("ruff", "format", "--check", "src/")
    # session.run("ruff", "format", "--check", "tests/")


@nox.session(python="3.14")
def typecheck(session: nox.Session) -> None:
    """Run the type checker."""
    session.install("-e", ".")
    session.install("ty")

    session.run("ty", "check", "src/")


# @nox.session(python="3.14")
# def test(session: nox.Session) -> None:
#    """Run the test suite."""
#    session.install("-e", ".")
#    session.install("pytest", "pytest-asyncio")
#    session.run("pytest", "tests/", "-v")
