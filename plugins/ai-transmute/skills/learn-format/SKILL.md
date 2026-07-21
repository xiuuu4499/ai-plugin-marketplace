---
name: learn-format
description: Learn or refresh an AI extension format from official documentation and local examples, then curate it into AI Transmute's OKF catalog. Use before enabling an unfamiliar platform, component type, manifest revision, hook schema, or notebook format.
---

# Learn an AI format

Use authoritative current sources and local installed examples. For OpenAI products, follow the official OpenAI documentation workflow. For other platforms, prefer their official documentation and schemas.

1. Inventory existing concepts with `okf index "$PLUGIN_ROOT/knowledge" --no-body` and `okf search`.
2. Use the OKF migrate playbook for local documents whose bodies must remain verbatim. Use OKF produce for concise, cited concepts derived from remote documentation.
3. Keep platform facts under `platforms/`, reusable semantics under `components/`, and equivalences or gaps under `mappings/`.
4. Update every affected index, timestamp, cross-link, and `log.md` entry.
5. Run `okf validate`, `okf lint`, `okf loose`, `okf tags --by area`, and `okf tags --by type`; then judge semantic consistency manually.

Do not enable a renderer from uncurated or uncited format knowledge.
