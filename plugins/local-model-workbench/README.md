# Local Model Workbench

Hybrid Codex/Kilo support for local-model work across llama.cpp, llama-swap, Qwen3.8, MiniMax H3, ComfyUI, VS Code, and MCP.

This plugin deliberately does not enforce Qwen sampler policy. Use `kilo-qwen38-generation-policy` for request-time Qwen3.8 parameter enforcement.

## Check Environment

```bash
plugins/local-model-workbench/scripts/local-model-workbench-check.sh
```

PowerShell:

```powershell
.\plugins\local-model-workbench\scripts\local-model-workbench-check.ps1
```

## Kilo Artifact

Install Kilo artifacts:

```bash
plugins/local-model-workbench/scripts/install-kilo-local-model-workbench.sh
```

PowerShell:

```powershell
.\plugins\local-model-workbench\scripts\install-kilo-local-model-workbench.ps1
```

Uninstall:

```bash
plugins/local-model-workbench/scripts/uninstall-kilo-local-model-workbench.sh
```

PowerShell:

```powershell
.\plugins\local-model-workbench\scripts\uninstall-kilo-local-model-workbench.ps1
```

The native implementations are Python files in `scripts/`; the shell and PowerShell files are thin wrappers.
