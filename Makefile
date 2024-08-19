version := $(shell python3 -c 'from jgtfxcon import version; print(version)')
SHELL := /bin/bash

.PHONY: venv
venv:
	[ -d .venv ] || virtualenv .venv --python=jgtfxcon
	conda activate jgtfxcon

.PHONY: piplocal
piplocal:
	pip install -e '.[dev]'

.PHONY: develop
develop: venv piplocal

.PHONY: lint lint-flake8 lint-isort
lint-flake8:
	flake8 test jgtfxcon
lint-isort:
	isort --check-only -rc jgtfxcon test *.py
lint: lint-flake8 lint-isort

.PHONY: format
format:
	isort -rc jgtfxcon test *.py

.PHONY: test
test:
	coverage run -m py.test
	coverage report

.PHONY: readme_check
readme_check:
	./setup.py check --restructuredtext --strict

.PHONY: rst_check
rst_check:
	make readme_check
	# Doesn't generate any output but prints out errors and warnings.
	make -C docs dummy

.PHONY: clean
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	rm -Rf dist
	rm -Rf *.egg-info

.PHONY: docs
docs:
	cd docs && make html

.PHONY: authors
authors:
	git log --format='%aN <%aE>' `git describe --abbrev=0 --tags`..@ | sort | uniq >> AUTHORS
	cat AUTHORS | sort --ignore-case | uniq >> AUTHORS_
	mv AUTHORS_ AUTHORS

.PHONY: dist
dist:
	make clean
	python setup.py sdist --format=gztar bdist_wheel

.PHONY: pypi-release
pypi-release:
	twine --version
	twine upload -s dist/*

.PHONY: release
release:
	make dist
	git tag -s $(version)
	git push origin $(version)
	make pypi-release

.PHONY: quick-release
quick-release:
	make bump_jgtutils
	make bump_version
	make dist
	make pypi-release
	
.PHONY: dev-pypi-release
dev-pypi-release:
	twine --version
	twine upload --repository pypi-dev dist/*

.PHONY: bump_jgtutils
bump_jgtutils:
	. /opt/binscripts/load.sh && _bump_jgtutils

.PHONY: bump_jgtfx2console
bump_jgtfx2console:
	bash bump_jgtfx2console.sh
	bash bump_jgtfx2console.sh

.PHONY: upbump_jgtfx2console_jgtutils
upbump_jgtfx2console_jgtutils:
	bash upbump_jgtfx2console_jgtutils.sh
	sleep 22
	make bump_jgtfx2console

.PHONY: bump_all
bump_all:
	make bump_jgtutils
	make bump_jgtfx2console

.PHONY: bump_version
bump_version:
	python bump_version.py
	git commit pyproject.toml jgtfxcon/__init__.py package.json -m bump:dev &>/dev/null

.PHONY: dev-release
dev-release:
	make bump_all
	make bump_version
	make dist
	make dev-pypi-release

.PHONY: dev-release-dk
dev-release-dk:
	make dev-release
	cd bin/dev && bash build.sh

.PHONY: dev-release-plus
dev-release-plus:
	make dev-release
	twine upload dist/*
