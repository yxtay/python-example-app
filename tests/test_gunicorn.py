import subprocess

import pytest
from pytest_mock import MockerFixture

try:
    from example_app import gunicorn
except ImportError as e:
    pytest.skip(e, allow_module_level=True)


def test_gunicorn_app(mocker: MockerFixture) -> None:
    mocker.patch("sys.argv", ["gunicorn"])
    gunicorn.Application()


def test_gunicorn_conf() -> None:
    argv = [
        "gunicorn",
        "--config",
        "python:example_app.gunicorn_conf",
        "--check-config",
    ]
    completed_process = subprocess.run(argv, check=False)  # noqa: S603
    assert completed_process.returncode == 0
