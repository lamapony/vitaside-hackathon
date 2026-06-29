# Repo-root shortcuts (frozen project).
.PHONY: help install test pytest demo serve-ui pages mcp-config

help:
	@./scripts/vitaside help

install:
	@./scripts/vitaside install

test:
	@./scripts/vitaside test

pytest:
	@./scripts/vitaside pytest

demo:
	@./scripts/vitaside demo

serve-ui:
	@./scripts/vitaside serve-ui

pages:
	@./scripts/vitaside pages

mcp-config:
	@./scripts/vitaside mcp-config
