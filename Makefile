

unit:
	@echo Running unit tests
	@echo "================="
	@python3 -m unittest discover -s tests -p "*_test.py" -v

test: unit

help:
	@echo Available targets are
	@echo - unit
	@echo - test

.DEFAULT_GOAL := help
.PHONY: unit
