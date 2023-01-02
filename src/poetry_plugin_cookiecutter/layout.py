
from collections.abc import Mapping
from pathlib import Path

from cookiecutter.main import cookiecutter
from poetry.layouts.layout import Layout
from tomlkit import loads
from tomlkit.toml_document import TOMLDocument


class CookieCutterLayout(Layout):
    _pyproject_toml = None
    _pyproject_toml_key = "pyproject_toml"

    def __init__(self,  *args, **kwargs):
        context = kwargs.pop('context', None)
        self._author_name = kwargs.pop('author_name', None)
        self._email = kwargs.pop('email', None)
        if context is None:
            context = dict()
        self._context = context
        default_content = self._context.get(self._pyproject_toml_key, self._pyproject_toml)
        if default_content is None:
            default_content = dict()
        elif isinstance(default_content, str):
            if Path(default_content).exists():
                with open(default_content) as f:
                    default_content = loads(f.read())
            else:
                default_content = loads(default_content)
        self._pyproject_toml = default_content
        self._cookiecutter_template = kwargs.pop('cookiecutter_template')
        # From context if needed
        super().__init__(*args, **kwargs)
        # Lets try to parse somethings here if we can
        for key in ['email', 'license', 'version', 'package_name', 'python']:
            for k in [key, key.capitalize(), key.upper()]:
                if k not in self._context and getattr(self, f'_{key}') is not None:
                    self._context[k] = getattr(self, f'_{key}')
        self._context['author'] = self._context.get('author', self._author_name)
        self._context['Author'] = self._context.get('Author', self._author_name)
        self._context['AUTHOR'] = self._context.get('AUTHOR', self._author_name)
        self._context['slug'] = self._context.get('slug', self._package_name)
        self._context['package_slug'] = self._context.get('package_slug', self._package_name)
        self._context['project_slug'] = self._context.get('project_slug ', self._package_name)
        self._context['project_name'] = self._context.get('project_name', self._project)
        self._context['name'] = self._context.get('name', self._project)

    def create(self, path: Path, with_tests: bool = True) -> None:
        # Cookiecutter here
        if self._cookiecutter_template is not None:
            path = Path(cookiecutter(self._cookiecutter_template, extra_context=self._context, output_dir=path))
            self._update_pyproject_toml(path)
            self._write_poetry(path) # - Write/update into pyproject.toml
            self._package_name = path.parts[-1]
        else:
            super().create(path, with_tests)
        return path

    def _update_pyproject_toml(self, path: Path):
        # We need to search for the pyproject_toml file in here if it exists
        if (path/'pyproject.toml').exists():
            with (path/'pyproject.toml').open() as f:
                cookiecutter_content = loads(f.read())
            self._pyproject_toml = _deep_update(self._pyproject_toml, cookiecutter_content)
            # Remove the file so we can write back to it
            (path/'pyproject.toml').unlink()

    def generate_poetry_content(self) -> TOMLDocument:
        # Merge in cookiecutter info
        return _deep_update(super().generate_poetry_content(), self._pyproject_toml)



def _deep_update(d, other):
    """Perform a deep update of a dictionary.

    Loop through each key in other and if both are dictionaries,
    then update the contents of the dictionary.
    """
    for key, value in other.items():
        d_value = d.get(key, None)
        if isinstance(value, Mapping) and isinstance(d_value, Mapping):
            d[key] = _deep_update(d_value, value)
        else:
            d[key] = value
    return d
