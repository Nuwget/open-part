VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: venv install run clean test

test: install
	$(PYTHON) -m unittest discover -s tests -v

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

run: install
	$(PYTHON) main.py

clean:
	rm -rf $(VENV)
