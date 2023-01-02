.PHONY: clean-pyc flake8 black bandit mypy format lint test coverage precommit install_build_tools build_package publish_package build_docs

flake8:
	poetry run flake8 src/ tests

black:
	poetry run black --check src/ tests

bandit:
	poetry run bandit src/ tests

mypy:
	poetry run mypy src/ tests

format:
	poetry run black src/ tests

lint: flake8 black bandit mypy

test:
	poetry run pytest tests -rs tests/unit --log-level=WARNING --cov=poetry_plugin_cookiecutter --cov-report html:{toxinidir}/reports/{envname}-coverage.html

coverage:
	poetry run coverage run --source src/poetry_plugin_cookiecutter -m pytest
	poetry run coverage report -m --fail-under=80
	poetry run coverage html

precommit:
	poetry run pre-commit run --all-files -v

install_build_tools:
	pip install --upgrade setuptools wheel twine

build_package: install_build_tools
	python setup.py sdist bdist_wheel

publish_package: build_package
	twine upload dist/*

clean_docs:
	find . -type d -name 'docs' -exec rm -fr {} +

create_doc_folder:
	mkdir docs/

copy_nojekyll:
	cp docsrc/.nojekyll docs/

build_docs:	clean_docs	create_doc_folder	copy_nojekyll
	sphinx-build -b html docsrc/source/ docs/

serve_docs:	build_docs
	python -m http.server --directory docs/

rebuild_docs:	clean_docs create_doc_folder
	sphinx-build -b html docsrc/source/ docs/
