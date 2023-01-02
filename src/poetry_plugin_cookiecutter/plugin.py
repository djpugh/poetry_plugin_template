from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_plugin_cookiecutter.command import CookiecutterCommand


if TYPE_CHECKING:
    from poetry.console.application import Application


def command_factory():
    return CookiecutterCommand()


class CookiecutterPlugin(ApplicationPlugin):

    def activate(self, application: Application) -> None:
        application.command_loader.register_factory("cookiecutter", command_factory)
