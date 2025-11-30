VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
CSV=$(VENV)/bin/csvdoctor

install:
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

example:
	$(CSV) inspect examples/broken.csv --html

clean:
	rm -rf outputs
