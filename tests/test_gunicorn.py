import subprocess
import sys

import pytest
from pytest_mock import MockerFixture

from example_app import gunicorn

pytest.importorskip("fcntl", reason="module not found: `fcntl`")


def test_gunicorn_app(mocker: MockerFixture) -> None:
    mocker.patch.object(sys, "argv", ["gunicorn"])
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
