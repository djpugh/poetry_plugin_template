from __future__ import annotations

from pathlib import Path
import sys

from contextlib import suppress

from cleo.helpers import argument
from cleo.helpers import option
from cookiecutter.cli import validate_extra_context
from poetry.console.commands.new import NewCommand



class CookiecutterCommand(NewCommand):
    name = "cookiecutter"
    description = "Creates a poetry object using cookiecutter."

    arguments = [argument("template", "The Cookiecutter template path to use."), argument('extra_context', multiple=True, optional=True)]
    options = [
        option("name", None, "Set the resulting package name.", flag=False),
        option("output-dir", "o","The path to create the project at.",  default='.', flag=False),
        option("checkout", "c", "The path to create the project at.", flag=False),
        option("replay", None, "The path to create the project at.", flag=False),
        option("replay-file", None, "The path to create the project at.", flag=False),
        option("overwrite-if-exists", "f", "The path to create the project at.", flag=False),
        option("skip-if-file-exists", "s", "The path to create the project at.", flag=False),
        option("config-file", None, "The path to create the project at.", flag=False),
        option("default-config", None, "The path to create the project at.", flag=True),
        option("debug-file", None, "The path to create the project at.", flag=False),
        option("accept-hooks", None, "The path to create the project at.", flag=False),
        option("list-installed", 'l', "The path to create the project at.", flag=False)
    ]

    def handle(self) -> int:
        from pathlib import Path

        from poetry.core.vcs.git import GitConfig

        from poetry.utils.env import SystemEnv

        from poetry_plugin_cookiecutter.layout import CookieCutterLayout
        if self.io.input.option("directory"):
            self.line_error(
                "<warning>--directory only makes sense with existing projects, and will"
                " be ignored. You should consider the option --path instead.</warning>"
            )


        path = Path(self.option("output-dir"))
        if not path.is_absolute():
            # we do not use resolve here due to compatibility issues
            # for path.resolve(strict=False)
            path = Path.cwd().joinpath(path)

        name = self.option("name")
        if not name:
            name = path.name

        if path.exists() and list(path.glob("*")):
            # Directory is not empty. Aborting.
            raise RuntimeError(
                f"Destination <fg=yellow>{path}</> exists and is not empty"
            )

        config = GitConfig()
        author = None
        author_name = None
        author_email = None
        if config.get("user.name"):
            author = config["user.name"]
            author_name = author
            author_email = config.get("user.email")
            if author_email:
                author += f" <{author_email}>"

        current_env = SystemEnv(Path(sys.executable))
        default_python = "^" + ".".join(str(v) for v in current_env.version_info[:2])

        layout_ = CookieCutterLayout(
            name,
            "0.1.0",
            author=author,
            email=author_email,
            author_name=author_name,
            python=default_python,
            cookiecutter_template=self.argument('template'),
            context=validate_extra_context(None, None, self.argument('extra_context'))
        )
        path = layout_.create(path)

        path = path.resolve()

        with suppress(ValueError):
            path = path.relative_to(Path.cwd())

        self.line(
            f"Created package <info>{layout_._package_name}</> in"
            f" <fg=blue>{path.as_posix()}</>"
        )

        return 0
