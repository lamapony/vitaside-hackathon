# VitaSide offline CI (VIT-45) — no real vault paths; demo-data only.
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
export OMI_VAULT_PATH ?= $(ROOT)/demo-data/vault
export VITASIDE_MANIFEST ?= $(ROOT)/sidecars/sleep-stress-sidecar/manifest.yaml
PYTHON ?= python3

.PHONY: ci deps issue-sidecars pytest mcporter expired mcp-selftest

ci: deps issue-sidecars pytest mcporter expired mcp-selftest
	@echo "=== make ci OK ==="

deps:
	$(PYTHON) -m pip install -q -U pip
	$(PYTHON) -m pip install -q -r requirements.txt -r requirements-dev.txt

issue-sidecars:
	./issue-sidecar.sh sleep-stress-sidecar >/dev/null

pytest:
	$(PYTHON) -m pytest tests/ -q \
		--cov=sidecar_protocol \
		--cov-report=term-missing \
		--cov-fail-under=80

mcporter:
	bash test-mcporter.sh

expired:
	bash test-mcporter-expired.sh

mcp-selftest:
	$(PYTHON) health-pattern-mcp.py --test