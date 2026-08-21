---
name: local-model-workbench
description: Plan, inspect, document, and troubleshoot local model workflows involving llama.cpp, llama-swap, Qwen3.8, MiniMax H3, ComfyUI, VS Code, Kilo Code, and MCP. Use when coordinating local inference/runtime setup rather than changing Qwen request generation policy itself.
---

# Local Model Workbench

Use this skill for local-model development workflows that span runtime launch, model aliases, VS Code/Kilo setup, ComfyUI, MiniMax H3, and MCP glue.

## Boundaries

The `kilo-qwen38-generation-policy` plugin is the enforcement layer for Qwen3.8 request parameters. Do not duplicate or override its sampler policy here.

This skill can help with:

- llama.cpp and llama-swap runtime planning;
- model alias and endpoint inventory;
- VS Code or Codespaces setup notes;
- ComfyUI/MiniMax H3 workflow decomposition;
- MCP integration planning;
- smoke-test scripts and reproducibility checklists.

Do not silently install model weights, ComfyUI nodes, or remote services. Treat large downloads and GPU/runtime changes as explicit user decisions.

## Workflow

1. Inventory the local environment and desired model path/alias/endpoint.
2. Separate runtime settings from request policy.
3. Confirm which component owns each concern: Kilo, Qwen policy plugin, llama-swap, llama.cpp, ComfyUI, MCP, or VS Code.
4. Produce commands or config snippets that are idempotent and easy to audit.
5. Verify with a small request, endpoint health check, or captured request body before declaring the setup done.

## Recommended Split

- Kilo: user interface, agent/session model selection, plugin hooks, skills, and provider config.
- Qwen policy plugin: per-request sampling, thinking flags, and reasoning effort.
- llama-swap: model routing and process switching.
- llama.cpp: runtime server, model file, context, GPU offload, Jinja/template support.
- ComfyUI: image/video graph execution and GPU scheduling.
- MiniMax H3: media generation prompt target and provider/MCP integration.
- VS Code/Codespaces: repeatable developer environment bootstrap.
