from pathlib import Path

import pytest
from briefcase.channels.base import BasePublicationChannel
from briefcase.exceptions import BriefcaseCommandError
from pythonanywhere_core.exceptions import (
    AuthenticationError,
    NoTokenError,
    PythonAnywhereApiException,
)

from briefcase_pythonanywhere import PythonAnywherePublicationChannel


def test_is_subclass_of_base():
    assert issubclass(PythonAnywherePublicationChannel, BasePublicationChannel)


def test_name_property():
    channel = PythonAnywherePublicationChannel()
    assert channel.name == "pythonanywhere"


def test_resolve_username_from_app_config(mock_app):
    mock_app.pythonanywhere_username = "configuser"
    channel = PythonAnywherePublicationChannel()
    assert channel._resolve_username(mock_app) == "configuser"


def test_resolve_username_falls_back_to_core(mock_app, mocker):
    mocker.patch(
        "briefcase_pythonanywhere.channel.get_username",
        return_value="coreuser",
    )
    channel = PythonAnywherePublicationChannel()
    assert channel._resolve_username(mock_app) == "coreuser"


def test_resolve_domain_from_app_config(mock_app):
    mock_app.pythonanywhere_domain = "custom.example.com"
    channel = PythonAnywherePublicationChannel()
    assert channel._resolve_domain(mock_app) == "custom.example.com"


def test_resolve_domain_default(mock_app):
    mock_app.pythonanywhere_username = "alice"
    channel = PythonAnywherePublicationChannel()
    assert channel._resolve_domain(mock_app) == "alice.pythonanywhere.com"


def test_publish_missing_zip_raises(mock_app, mock_command):
    mock_app.pythonanywhere_username = "testuser"
    mock_command.distribution_path.return_value = (
        mock_command.dist_path / "nonexistent.zip"
    )

    channel = PythonAnywherePublicationChannel()
    with pytest.raises(BriefcaseCommandError, match="Distribution artifact not found"):
        channel.publish_app(mock_app, mock_command)


def test_publish_missing_api_token(mock_app, mock_command, dist_zip, mocker):
    mock_app.pythonanywhere_username = "testuser"

    mocker.patch(
        "briefcase_pythonanywhere.channel.Files"
    ).return_value.tree_post.side_effect = NoTokenError("no token")

    channel = PythonAnywherePublicationChannel()
    with pytest.raises(BriefcaseCommandError, match="API token not found"):
        channel.publish_app(mock_app, mock_command)


def test_publish_auth_error(mock_app, mock_command, dist_zip, mocker):
    mock_app.pythonanywhere_username = "testuser"

    mocker.patch(
        "briefcase_pythonanywhere.channel.Files"
    ).return_value.tree_post.side_effect = AuthenticationError("bad token")

    channel = PythonAnywherePublicationChannel()
    with pytest.raises(BriefcaseCommandError, match="authentication failed"):
        channel.publish_app(mock_app, mock_command)


def test_publish_creates_new_webapp(mock_app, mock_command, dist_zip, mocker):
    mock_app.pythonanywhere_username = "testuser"

    mock_files_cls = mocker.patch("briefcase_pythonanywhere.channel.Files")
    mock_webapp_cls = mocker.patch("briefcase_pythonanywhere.channel.Webapp")
    mock_webapp = mock_webapp_cls.return_value
    mock_webapp.get.side_effect = PythonAnywhereApiException("not found")

    channel = PythonAnywherePublicationChannel()
    channel.publish_app(mock_app, mock_command)

    # Files uploaded to correct remote path
    mock_files_cls.return_value.tree_post.assert_called_once()
    _, remote_path = mock_files_cls.return_value.tree_post.call_args[0]
    assert remote_path == "/home/testuser/myapp"

    # Webapp created for correct domain
    mock_webapp_cls.assert_called_with("testuser.pythonanywhere.com")
    mock_webapp.create.assert_called_once()

    # Static file mapping set and webapp reloaded
    mock_webapp.create_static_file_mapping.assert_called_once_with(
        "/", Path("/home/testuser/myapp")
    )
    mock_webapp.reload.assert_called_once()


def test_publish_sets_pythonanywhere_client_env(
    mock_app, mock_command, dist_zip, mocker, monkeypatch
):
    mock_app.pythonanywhere_username = "testuser"
    monkeypatch.delenv("PYTHONANYWHERE_CLIENT", raising=False)

    mocker.patch("briefcase_pythonanywhere.channel.Files")
    mock_webapp_cls = mocker.patch("briefcase_pythonanywhere.channel.Webapp")
    mock_webapp_cls.return_value.get.return_value = {"id": 1}

    import os

    import briefcase_pythonanywhere

    channel = PythonAnywherePublicationChannel()
    channel.publish_app(mock_app, mock_command)

    assert os.environ["PYTHONANYWHERE_CLIENT"] == (
        f"briefcase-pythonanywhere/{briefcase_pythonanywhere.__version__}"
    )


def test_publish_extracts_zip_before_upload(mock_app, mock_command, dist_zip, mocker):
    mock_app.pythonanywhere_username = "testuser"

    mock_files_cls = mocker.patch("briefcase_pythonanywhere.channel.Files")
    mock_webapp_cls = mocker.patch("briefcase_pythonanywhere.channel.Webapp")
    mock_webapp_cls.return_value.get.return_value = {"id": 1}

    uploaded_local_dir = None

    def capture_tree_post(local_dir: str, remote_dir: str) -> None:
        nonlocal uploaded_local_dir
        uploaded_local_dir = local_dir
        local = Path(local_dir)
        assert (local / "index.html").exists()
        assert (local / "static" / "css" / "style.css").exists()

    mock_files_cls.return_value.tree_post.side_effect = capture_tree_post

    channel = PythonAnywherePublicationChannel()
    channel.publish_app(mock_app, mock_command)

    assert uploaded_local_dir is not None


def test_publish_api_error_wrapped(mock_app, mock_command, dist_zip, mocker):
    mock_app.pythonanywhere_username = "testuser"

    mocker.patch(
        "briefcase_pythonanywhere.channel.Files"
    ).return_value.tree_post.side_effect = PythonAnywhereApiException("upload failed")

    channel = PythonAnywherePublicationChannel()
    with pytest.raises(BriefcaseCommandError, match="PythonAnywhere API error"):
        channel.publish_app(mock_app, mock_command)


def test_publish_updates_existing_webapp(mock_app, mock_command, dist_zip, mocker):
    mock_app.pythonanywhere_username = "testuser"

    mocker.patch("briefcase_pythonanywhere.channel.Files")
    mock_webapp_cls = mocker.patch("briefcase_pythonanywhere.channel.Webapp")
    mock_webapp = mock_webapp_cls.return_value
    mock_webapp.get.return_value = {"id": 123}

    channel = PythonAnywherePublicationChannel()
    channel.publish_app(mock_app, mock_command)

    # Webapp NOT created (already exists)
    mock_webapp.create.assert_not_called()

    # Static mapping and reload still happen
    mock_webapp.create_static_file_mapping.assert_called_once_with(
        "/", Path("/home/testuser/myapp")
    )
    mock_webapp.reload.assert_called_once()
