from __future__ import annotations

import zipfile

import pytest


@pytest.fixture()
def mock_command(tmp_path, mocker):
    """A mock object satisfying the PublishCommandAPI protocol."""
    command = mocker.MagicMock()
    command.dist_path = tmp_path / "dist"
    command.dist_path.mkdir()
    return command


@pytest.fixture()
def mock_app(mocker):
    """A minimal AppConfig-like object."""
    app = mocker.MagicMock()
    app.app_name = "myapp"
    app.formal_name = "My App"
    app.version = "1.0.0"
    # No pythonanywhere-specific config by default
    del app.pythonanywhere_username
    del app.pythonanywhere_domain
    del app.pythonanywhere_directory
    return app


@pytest.fixture()
def dist_zip(mock_command, mock_app):
    """Create a sample distribution ZIP and wire command.distribution_path to it."""
    zip_name = f"{mock_app.formal_name}-{mock_app.version}.web.zip"
    zip_path = mock_command.dist_path / zip_name
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("index.html", "<html><body>Hello</body></html>")
        zf.writestr("static/css/style.css", "body { margin: 0; }")
    mock_command.distribution_path.return_value = zip_path
    return zip_path
