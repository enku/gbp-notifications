.SHELL := /bin/bash

name := $(shell pdm show --name)
version := $(shell pdm show --version)
sdist := dist/$(name)-$(version).tar.gz
wheel := dist/$(subst -,_,$(name))-$(version)-py3-none-any.whl
src := $(shell find src -type f -print)
tests := $(shell find tests -type f -print)
python_src := $(filter %.py, $(src) $(tests))

PYTHONDONTWRITEBYTECODE=1

export PYTHONDONTWRITEBYTECODE


.coverage: $(src) $(tests)
	coverage run -m tests

test: .coverage
.PHONY: test


coverage-report: .coverage
	coverage html
	python -m webbrowser -t file://$(CURDIR)/htmlcov/index.html

build: $(sdist) $(wheel)

wheel: $(wheel)
.PHONY: wheel


sdist: $(sdist)
.PHONY: sdist


$(sdist): $(src)
	pdm build --no-wheel

$(wheel): $(src)
	pdm build --no-sdist

clean: clean-build clean-venv
	rm -rf .coverage .fmt htmlcov .mypy_cache node_modules
.PHONY: clean


clean-build:
	rm -rf dist build
.PHONY: clean-build


clean-venv:
	rm -rf .venv
.PHONY: clean-venv


pylint:
	pylint src tests
.PHONY: pylint


mypy:
	mypy
.PHONY: mypy


lint: pylint mypy
.PHONY: lint


.fmt: $(python_src)
	pdm run python -m isort --line-width=88 $?
	pdm run python -m black $?
	touch $@


.PHONY: fmt
fmt: .fmt
