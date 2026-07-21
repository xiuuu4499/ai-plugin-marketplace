---
name: transform
description: Semantically redesign AI skills, plugins, hooks, agents, or notebook workflows while retaining an auditable relationship to the source. Use when responsibilities, workflows, tools, or architecture must change rather than merely being reformatted.
---

# Transform an AI workflow

1. Use `$inspect` and `$plan` to establish the source behavior and portability baseline.
2. Write the requested semantic changes into a job OKF concept before editing output.
3. Use `$convert` to create the closest target package, then apply the redesign only inside `package/`.
4. Update the job's mapping and loss concepts plus `report.md`; distinguish requested redesigns from target-format losses.
5. Run `$validate` and `$diff` before completion.

Do not call a semantic redesign a lossless conversion.
