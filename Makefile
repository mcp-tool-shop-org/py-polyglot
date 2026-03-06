.PHONY: verify test build clean

verify: test build
	@echo "All checks passed."

test:
	python -m pytest tests/ -v

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
