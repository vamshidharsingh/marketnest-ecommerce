PYTHON ?= python3
.PHONY: run test smoke verify
run:
	$(PYTHON) -B -m app
test:
	$(PYTHON) -B -m unittest discover -s tests -v
smoke:
	$(PYTHON) -B scripts/smoke_test.py
verify:
	$(PYTHON) -B scripts/verify_files.py
