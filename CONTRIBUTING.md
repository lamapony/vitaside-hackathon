# Contributing

**Project status: Frozen (June 2026).** Not actively maintained.

You are welcome to fork and experiment. For a working baseline:

```bash
git clone https://github.com/lamapony/vitaside-hackathon.git
cd vitaside-hackathon
make install
make test
```

Before opening a PR on this repo, note that maintainers may not merge unless the project unfreezes.

**Guidelines if you fork:**

- Do not commit personal health exports, vault paths, or `mcp-config.local.json`
- Run `make test` and `make pytest` before sharing changes
- Keep sidecar manifests scoped and TTL-bound

**Docs:** [docs/AGENT-ONBOARDING.md](docs/AGENT-ONBOARDING.md) · [STATUS.md](STATUS.md)

License: MIT ([LICENSE](LICENSE))
