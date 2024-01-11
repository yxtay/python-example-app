from typer.testing import CliRunner

from example_app.settings import app


def test_settings_cli_valid() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["app_name"])
    assert result.exit_code == 0
    assert "example_app" in result.stdout


def test_settings_cli_invalid() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["none"])
    assert result.exit_code == 0
    assert result.stdout == ""
