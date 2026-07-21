# AI Plugin Marketplace

A dedicated Codex marketplace for portable AI-extension tooling. It currently ships two plugins:

| Plugin | Purpose |
| --- | --- |
| `okf` | Author, search, migrate, validate, lint, maintain, and curate [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) bundles. |
| `ai-transmute` | Inspect and convert AI skills, commands, agents, hooks, plugins, instruction files, MCP/LSP configuration, and notebooks through auditable OKF intermediates. |

The marketplace lives at [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json). Both plugins are maintained in this repository and published by [xiuuu4499](https://github.com/xiuuu4499).

## Scope

AI Transmute understands Codex, Claude, GitHub Copilot, Grok Build, and Gemini CLI packaging. Its workflow is deliberately loss-aware:

1. Inventory the source without changing it.
2. Retrieve the relevant platform and component knowledge.
3. Create and curate an OKF audit bundle for the conversion job.
4. Render the target package.
5. Validate the result and report exact mappings, approximations, omissions, and manual follow-ups.

Conversions are written to a new timestamped directory and contain:

```text
ai-transmute/<timestamp>-<source>-to-<target>/
├── package/     # converted target artifact
├── okf/         # portable conversion record
├── report.md    # fidelity and validation report
└── job.json     # machine-readable job metadata
```

Jupyter notebooks retain their cells, metadata, attachments, and code. Hosted AI notebooks or projects without a documented portable import API are rendered as import packs with manual setup instructions.

## Install Codex CLI in a Codespace

OpenAI's current macOS/Linux recommendation is the standalone installer. It installs in user space and does not require rebuilding or restarting the devcontainer:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
hash -r
codex --version
```

The standard Codespaces `PATH` already includes `~/.local/bin`. If a customized image does not, activate it in the current shell:

```bash
export PATH="$HOME/.local/bin:$PATH"
hash -r
```

Run `codex` once and select a supported sign-in method if the CLI requests authentication.

For reproducible future container builds, put the same installer command in the consuming repository's devcontainer setup. That is optional for the current container and only takes effect on a later create or rebuild.

## Install this marketplace

From the root of this clone:

```bash
codex plugin marketplace add "$PWD"
codex plugin add okf@ai-plugin-marketplace
codex plugin add ai-transmute@ai-plugin-marketplace
```

Start a new Codex thread after installation so newly installed skills and hooks are loaded. The advisory hooks are fail-open: they provide capped validation context but do not rewrite files or grant permissions.

## Plugin entry points

The `okf` plugin exposes the full OKF workflow plus a thin `gem` command router.

AI Transmute exposes these skills:

- `inspect` — detect the platform, components, dependencies, and portability hazards without writing output.
- `plan` — produce a dry-run mapping and predicted loss report.
- `convert` — perform a format-preserving conversion through an OKF job bundle.
- `extract` — pull selected components from a package or extrapolate a package from a smaller artifact.
- `transform` — redesign behavior while explicitly recording semantic changes.
- `learn-format` — curate official specifications and local examples before enabling a format.
- `feedback` — correct durable format knowledge, mappings, renderer behavior, or one conversion job.
- `validate` — check sources, OKF bundles, target packages, and complete jobs.
- `diff` — compare behavior and component inventories rather than filenames alone.
- `doctor` — report required and optional runtime availability.

## Requirements

- Python 3 for AI Transmute's deterministic engine and advisory hook.
- The `okf` CLI for audited conversion and knowledge-catalog workflows.
- Ruby for the OKF plugin's advisory curation hook.
- Target-native CLIs are optional; when present, validation can use them in addition to internal checks.

Missing optional tools are reported rather than installed automatically.

## Development and validation

Run the deterministic test suite:

```bash
python3 -m unittest discover -s plugins/ai-transmute/tests -v
```

Validate the persistent knowledge catalog:

```bash
okf validate plugins/ai-transmute/knowledge
okf lint plugins/ai-transmute/knowledge
okf loose plugins/ai-transmute/knowledge
```

Plugin manifests and skill folders can additionally be checked with the validators bundled with Codex's `plugin-creator` and `skill-creator` skills.

## License

Repository-authored code and documentation are available under the [MIT License](LICENSE). Vendored OKF reference material retains its upstream Apache 2.0 notice in [`plugins/okf/skills/okf/reference/APACHE-2.0.txt`](plugins/okf/skills/okf/reference/APACHE-2.0.txt).
