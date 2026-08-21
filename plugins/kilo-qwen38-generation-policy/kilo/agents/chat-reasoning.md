---
description: Analytical chat for comparisons, synthesis, multi-step reasoning, and nontrivial decisions.
mode: primary
model: local-qwen/qwen3.8-27b
requirements:
  skills:
    - qwen38-generation-policy
permission:
  edit: deny
  bash: deny
---

Use medium reasoning by default. Escalate subsequent/delegated work to xhigh only when complexity warrants it.
