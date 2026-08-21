# Kilo Qwen3.8 Generation Policy

This Codex marketplace plugin ships a global Kilo Code integration for Qwen3.8 request policy.

## Install For Kilo

```bash
plugins/kilo-qwen38-generation-policy/scripts/install-kilo-qwen38-policy.sh
```

PowerShell:

```powershell
.\plugins\kilo-qwen38-generation-policy\scripts\install-kilo-qwen38-policy.ps1
```

The installer copies only owned files into the Kilo global config directory. Run `/reload` in Kilo or restart Kilo afterwards.

Override the install target for tests:

```bash
KILO_TARGET_CONFIG_DIR=/tmp/kilo-test plugins/kilo-qwen38-generation-policy/scripts/install-kilo-qwen38-policy.sh
```

The native implementation is `scripts/install-kilo-qwen38-policy.py`; the shell and PowerShell files are thin wrappers around it.

## Uninstall

```bash
plugins/kilo-qwen38-generation-policy/scripts/uninstall-kilo-qwen38-policy.sh
```

PowerShell:

```powershell
.\plugins\kilo-qwen38-generation-policy\scripts\uninstall-kilo-qwen38-policy.ps1
```

Uninstall uses the manifest written at install time and removes only owned files.

## Provider Setup

Configure Kilo with an OpenAI-compatible local provider/model such as `local-qwen/qwen3.8-27b`. A safe example lives at `scripts/qwen38-provider.example.jsonc`; the installer does not merge it automatically.

## Manual Verification

Check plugin/agent/skill discovery after install from:

- an empty directory;
- a single-root Git repository;
- a repository without `.kilo`;
- a repository with its own `.kilo`;
- a multi-root VS Code workspace.

For request-level verification, point Kilo at a mock OpenAI-compatible server and inspect the JSON body for the managed fields documented in the skill.
