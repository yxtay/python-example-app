import subprocess

from example_app import gunicorn


def test_gunicorn_app() -> None:
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
