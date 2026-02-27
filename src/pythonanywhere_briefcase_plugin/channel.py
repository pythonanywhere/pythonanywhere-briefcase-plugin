from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZipFile

from briefcase.channels.base import BasePublicationChannel
from briefcase.exceptions import BriefcaseCommandError
from pythonanywhere_core.base import get_username
from pythonanywhere_core.exceptions import (
    AuthenticationError,
    NoTokenError,
    PythonAnywhereApiException,
)
from pythonanywhere_core.files import Files
from pythonanywhere_core.webapp import Webapp

import pythonanywhere_briefcase_plugin

if TYPE_CHECKING:
    from briefcase.channels.base import PublishCommandAPI
    from briefcase.config import AppConfig


class PythonAnywherePublicationChannel(BasePublicationChannel):
    @property
    def name(self) -> str:
        return "pythonanywhere"

    def _resolve_username(self, app: AppConfig) -> str:
        username = getattr(app, "pythonanywhere_username", None)
        if username:
            return username

        return get_username()

    def _resolve_domain(self, app: AppConfig) -> str:
        domain = getattr(app, "pythonanywhere_domain", None)
        if domain:
            return domain

        username = self._resolve_username(app)
        return f"{username}.pythonanywhere.com"

    def publish_app(self, app: AppConfig, command: PublishCommandAPI, **options):
        dist_path = command.distribution_path(app)
        if not dist_path.exists():
            raise BriefcaseCommandError(
                f"Distribution artifact not found: {dist_path}\n\n"
                "Run 'briefcase package web static' first."
            )

        os.environ["PYTHONANYWHERE_CLIENT"] = (
            f"pythonanywhere-briefcase-plugin/{pythonanywhere_briefcase_plugin.__version__}"
        )

        username = self._resolve_username(app)
        domain = self._resolve_domain(app)
        remote_path = getattr(app, "pythonanywhere_directory", None)
        if not remote_path:
            remote_path = f"/home/{username}/{app.app_name}"

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with ZipFile(dist_path) as zf:
                    zf.extractall(tmpdir)
                Files().tree_post(tmpdir, remote_path)

            webapp = Webapp(domain)
            try:
                webapp.get()
            except PythonAnywhereApiException:
                webapp.create(
                    python_version="3.13",
                    virtualenv_path=None,
                    project_path=Path(remote_path),
                    nuke=False,
                )

            webapp.create_static_file_mapping("/", Path(remote_path))
            webapp.reload()
        except NoTokenError as e:
            raise BriefcaseCommandError(
                "PythonAnywhere API token not found.\n\n"
                "Set the API_TOKEN environment variable with "
                "your token from\n"
                "https://www.pythonanywhere.com/account/#api_token"
            ) from e
        except AuthenticationError as e:
            raise BriefcaseCommandError(
                "PythonAnywhere API authentication failed.\n\n"
                "Check that your API_TOKEN environment variable "
                "contains a valid token."
            ) from e
        except PythonAnywhereApiException as e:
            raise BriefcaseCommandError(f"PythonAnywhere API error: {e}") from e
