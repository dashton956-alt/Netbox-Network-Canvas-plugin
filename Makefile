VENV_PYTHON = /opt/netbox/venv/bin/python
PIP = $(VENV_PYTHON) -m pip
MANAGE = $(VENV_PYTHON) /opt/netbox/netbox/manage.py

.PHONY: help install-test-deps run-shell-test run-pytest junit shell-junit

help:
	@echo "Makefile for dev integration tests"
	@echo "install-test-deps  - install pytest and pytest-django into NetBox venv"
	@echo "run-shell-test      - run integration tests via manage.py shell (fast, no pytest required)"
	@echo "run-pytest          - run tests with pytest inside the NetBox venv"
	@echo "junit               - run pytest and emit junit xml to ./junit-report.xml"

install-test-deps:
	@echo Installing pytest and pytest-django into the NetBox venv...
	sudo $(PIP) install pytest pytest-django

run-shell-test:
	@echo Running integration tests via manage.py shell (requires RUN_PLUGIN_INTEGRATION_TESTS=1)...
	RUN_PLUGIN_INTEGRATION_TESTS=1 sudo $(VENV_PYTHON) /opt/netbox/netbox/manage.py shell < $(CURDIR)/tests/test_integration_api_extended.py


run-pytest:
	@echo Running pytest inside NetBox venv (requires pytest installed with install-test-deps)...
	cd /opt/netbox && sudo -E sh -c 'RUN_PLUGIN_INTEGRATION_TESTS=1 env PYTHONPATH=/opt/netbox/netbox "$(VENV_PYTHON)" -m pytest "$(CURDIR)/tests" -q'


junit:
	@echo Running pytest and producing junit-report.xml
	cd /opt/netbox && sudo -E sh -c 'RUN_PLUGIN_INTEGRATION_TESTS=1 env PYTHONPATH=/opt/netbox/netbox "$(VENV_PYTHON)" -m pytest "$(CURDIR)/tests" -q --junitxml="$(CURDIR)/junit-report.xml"'

shell-junit:
	@echo Running integration runner via manage.py shell and producing junit-report.xml (no test DB creation)
	cd /opt/netbox && sudo -E sh -c '"$(VENV_PYTHON)" /opt/netbox/netbox/manage.py shell < "$(CURDIR)/tests/run_integration_runner.py"'

sources = NetBox Network Canvas Plugin

.PHONY: test format lint unittest pre-commit clean
test: format lint unittest

format:
	isort $(sources) tests
	black $(sources) tests

lint:
	flake8 $(sources) tests

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site
