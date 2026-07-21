#!/usr/bin/env python3
"""Deterministic inventory, rendering, and validation for AI Transmute."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


PLATFORMS = ("codex", "claude", "copilot", "grok", "gemini", "generic")
TARGETS = PLATFORMS[:-1]
KINDS = (
    "plugin", "skill", "command", "hook", "agent", "mcp", "lsp",
    "instruction", "automation", "jupyter-notebook", "hosted-notebook",
)
SUPPORT = {
    "codex": {"plugin", "skill", "hook", "mcp", "instruction", "jupyter-notebook", "hosted-notebook"},
    "claude": {"plugin", "skill", "command", "hook", "agent", "mcp", "lsp", "instruction", "jupyter-notebook", "hosted-notebook"},
    "copilot": {"plugin", "skill", "hook", "agent", "mcp", "lsp", "instruction", "jupyter-notebook", "hosted-notebook"},
    "grok": {"plugin", "skill", "command", "hook", "agent", "mcp", "lsp", "instruction", "jupyter-notebook", "hosted-notebook"},
    "gemini": {"plugin", "skill", "command", "hook", "agent", "mcp", "instruction", "automation", "jupyter-notebook", "hosted-notebook"},
}
EVENTS = {
    "codex": {"pre": "PreToolUse", "post": "PostToolUse", "start": "SessionStart", "stop": "Stop"},
    "claude": {"pre": "PreToolUse", "post": "PostToolUse", "start": "SessionStart", "stop": "Stop"},
    "grok": {"pre": "PreToolUse", "post": "PostToolUse", "start": "SessionStart", "stop": "Stop"},
    "copilot": {"pre": "preToolUse", "post": "postToolUse", "start": "sessionStart", "stop": "agentStop"},
    "gemini": {"pre": "BeforeTool", "post": "AfterTool", "start": "SessionStart", "stop": "AfterAgent"},
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    return sorted(p for p in source.rglob("*") if p.is_file() and ".git" not in p.parts)


def rel(path: Path, root: Path) -> str:
    return path.name if root.is_file() else path.relative_to(root).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_platform(source: Path, files: list[Path]) -> tuple[str, list[str]]:
    names = {rel(p, source) for p in files}
    signals: list[str] = []
    if ".codex-plugin/plugin.json" in names:
        signals.append(".codex-plugin/plugin.json")
        return "codex", signals
    if "gemini-extension.json" in names:
        signals.append("gemini-extension.json")
        return "gemini", signals
    if ".claude-plugin/plugin.json" in names:
        signals.append(".claude-plugin/plugin.json")
        return "claude", signals
    if "plugin.json" in names:
        signals.append("plugin.json")
        return "copilot", signals
    if any(n.startswith(".grok/") for n in names):
        signals.append(".grok/")
        return "grok", signals
    if any(n.startswith(".claude/") for n in names):
        signals.append(".claude/")
        return "claude", signals
    if any(n.startswith(".github/") for n in names):
        signals.append(".github/")
        return "copilot", signals
    if any(n.startswith(".gemini/") for n in names):
        signals.append(".gemini/")
        return "gemini", signals
    if any(p.name == "SKILL.md" for p in files):
        signals.append("SKILL.md")
    return "generic", signals


def detect_kinds(source: Path, files: list[Path]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {kind: [] for kind in KINDS}
    for path in files:
        name = rel(path, source)
        parts = set(Path(name).parts)
        low = name.lower()
        if low.endswith("plugin.json") or low == "gemini-extension.json":
            found["plugin"].append(name)
        if path.name == "SKILL.md" or "skills" in parts:
            found["skill"].append(name)
        if "commands" in parts and path.suffix.lower() in {".md", ".toml"}:
            found["command"].append(name)
        if "hooks" in parts or path.name in {"hooks.json", "hook.json"}:
            found["hook"].append(name)
        if "agents" in parts and path.name != "openai.yaml":
            found["agent"].append(name)
        if path.name in {".mcp.json", "mcp.json"}:
            found["mcp"].append(name)
        if path.name == "lsp.json":
            found["lsp"].append(name)
        if path.name in {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "GROK.md"}:
            found["instruction"].append(name)
        if "automation" in low or "trigger" in low:
            found["automation"].append(name)
        if path.suffix.lower() == ".ipynb":
            found["jupyter-notebook"].append(name)
        if "notebook" in low and path.suffix.lower() != ".ipynb":
            found["hosted-notebook"].append(name)
    return {kind: sorted(set(paths)) for kind, paths in found.items() if paths}


def notebook_details(source: Path, files: list[Path]) -> list[dict[str, Any]]:
    details = []
    for path in files:
        if path.suffix.lower() != ".ipynb":
            continue
        item: dict[str, Any] = {"path": rel(path, source), "valid_json": False}
        try:
            data = read_json(path)
            cells = data.get("cells", [])
            item.update({
                "valid_json": isinstance(cells, list),
                "nbformat": data.get("nbformat"),
                "cells": len(cells) if isinstance(cells, list) else 0,
                "cell_types": [c.get("cell_type") for c in cells if isinstance(c, dict)],
                "metadata_keys": sorted(data.get("metadata", {}).keys()) if isinstance(data.get("metadata"), dict) else [],
            })
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            item["error"] = str(exc)
        details.append(item)
    return details


def inspect_source(source_arg: str) -> dict[str, Any]:
    source = Path(source_arg).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    files = text_files(source)
    platform, signals = detect_platform(source, files)
    return {
        "source": str(source),
        "source_type": "file" if source.is_file() else "directory",
        "platform": platform,
        "signals": signals,
        "kinds": detect_kinds(source, files),
        "notebooks": notebook_details(source, files),
        "file_count": len(files),
        "files": [{"path": rel(p, source), "sha256": sha256(p), "size": p.stat().st_size} for p in files],
    }


def plan_conversion(inventory: dict[str, Any], target: str) -> dict[str, Any]:
    exact, approximations, losses = [], [], []
    for kind in sorted(inventory["kinds"]):
        if kind == "hook" and inventory["platform"] not in {target, "generic"}:
            approximations.append({"kind": kind, "strategy": "translate event names, then audit payload, matcher, timeout, trust, and output semantics"})
        elif kind in SUPPORT[target]:
            exact.append({"kind": kind, "strategy": "preserve or render native target structure"})
        elif kind == "command" and target == "codex":
            approximations.append({"kind": kind, "strategy": "render each command as a user-invocable Agent Skill"})
        elif kind == "agent" and target == "codex":
            approximations.append({"kind": kind, "strategy": "render agent instructions as a dedicated skill"})
        elif kind == "lsp" and target in {"codex", "gemini"}:
            losses.append({"kind": kind, "reason": "no documented plugin-native LSP component"})
        else:
            losses.append({"kind": kind, "reason": f"no exact {target} renderer"})
    if target == "grok":
        approximations.append({"kind": "plugin", "strategy": "emit a Claude-compatible plugin, which Grok loads natively"})
    if inventory["kinds"].get("hosted-notebook"):
        approximations.append({"kind": "hosted-notebook", "strategy": "emit a portable import pack and manual setup instructions"})
    return {
        "source_platform": inventory["platform"],
        "target": target,
        "exact": exact,
        "approximations": approximations,
        "losses": losses,
        "manual_follow_up": bool(approximations or losses or inventory["kinds"].get("hosted-notebook")),
    }


def copy_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)


def source_name(source: Path) -> str:
    stem = source.stem if source.is_file() else source.name
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-") or "artifact"


def load_manifest(source: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    candidates = {
        "codex": source / ".codex-plugin" / "plugin.json",
        "claude": source / ".claude-plugin" / "plugin.json",
        "copilot": source / "plugin.json",
        "gemini": source / "gemini-extension.json",
    }
    path = candidates.get(inventory["platform"])
    if path and path.is_file():
        try:
            return read_json(path)
        except (ValueError, json.JSONDecodeError):
            pass
    return {}


def manifest_identity(source: Path, inventory: dict[str, Any]) -> tuple[str, str, str]:
    manifest = load_manifest(source, inventory) if source.is_dir() else {}
    name = re.sub(r"[^a-z0-9]+", "-", str(manifest.get("name") or source_name(source)).lower()).strip("-")
    version = str(manifest.get("version") or "0.1.0")
    description = str(manifest.get("description") or f"Converted {name} artifact")
    return name or "converted-artifact", version, description


def skill_frontmatter(name: str, description: str, body: str) -> str:
    safe = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "converted-skill"
    desc = description.replace("\n", " ").strip() or f"Converted workflow for {safe}."
    return f"---\nname: {safe}\ndescription: {desc}\n---\n\n{body.strip()}\n"


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:].lstrip()
    return text


def copy_skills(source: Path, package: Path, inventory: dict[str, Any]) -> None:
    for item in inventory["kinds"].get("skill", []):
        path = source if source.is_file() else source / item
        if path.name != "SKILL.md":
            continue
        if source.is_file():
            destination = package / "skills" / source_name(source) / "SKILL.md"
        else:
            parts = Path(item).parts
            try:
                idx = parts.index("skills")
                destination = package / "skills" / Path(*parts[idx + 1:])
            except ValueError:
                destination = package / "skills" / path.parent.name / "SKILL.md"
        copy_path(path, destination)
        for sibling in path.parent.iterdir():
            if sibling.name != "SKILL.md" and source.is_dir():
                copy_path(sibling, destination.parent / sibling.name)


def render_commands(source: Path, package: Path, inventory: dict[str, Any], target: str) -> None:
    for item in inventory["kinds"].get("command", []):
        path = source / item
        body = path.read_text(encoding="utf-8", errors="replace")
        name = path.stem
        if target == "gemini":
            destination = package / "commands" / Path(item).relative_to("commands")
            destination = destination.with_suffix(".toml")
            destination.parent.mkdir(parents=True, exist_ok=True)
            escaped = body.replace('"""', '\\\"\\\"\\\"')
            destination.write_text(f'prompt = """\n{escaped}\n"""\n', encoding="utf-8")
        elif target == "codex":
            destination = package / "skills" / name / "SKILL.md"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(skill_frontmatter(name, f"Converted command {name}. Use when this workflow is requested explicitly.", strip_frontmatter(body)), encoding="utf-8")
        else:
            copy_path(path, package / item)


def render_agents(source: Path, package: Path, inventory: dict[str, Any], target: str) -> None:
    for item in inventory["kinds"].get("agent", []):
        path = source / item
        if target == "codex":
            name = f"agent-{path.stem.replace('.agent', '')}"
            body = path.read_text(encoding="utf-8", errors="replace")
            dest = package / "skills" / name / "SKILL.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(skill_frontmatter(name, f"Converted agent instructions from {path.name}.", strip_frontmatter(body)), encoding="utf-8")
        elif "agent" in SUPPORT[target]:
            copy_path(path, package / item)


def normalize_event(event: str, target: str) -> str:
    low = event.lower()
    role = "post" if "posttool" in low or "aftertool" in low else "pre" if "pretool" in low or "beforetool" in low else "start" if "sessionstart" in low else "stop"
    return EVENTS[target][role]


def render_hooks(source: Path, package: Path, inventory: dict[str, Any], target: str) -> None:
    configs = []
    for item in inventory["kinds"].get("hook", []):
        path = source / item
        if path.suffix == ".json":
            try:
                data = read_json(path)
                if isinstance(data.get("hooks"), dict):
                    configs.append(data["hooks"])
            except (ValueError, json.JSONDecodeError):
                continue
        elif path.is_file():
            copy_path(path, package / "hooks" / "scripts" / path.name)
    if not configs:
        return
    merged: dict[str, list[Any]] = {}
    for config in configs:
        for event, entries in config.items():
            if isinstance(entries, list):
                merged.setdefault(normalize_event(event, target), []).extend(entries)
    payload: dict[str, Any] = {"hooks": merged}
    if target == "copilot":
        payload["version"] = 1
    write_json(package / "hooks" / "hooks.json", payload)


def copy_named_components(source: Path, package: Path, inventory: dict[str, Any], target: str) -> None:
    for kind, filename in (("mcp", ".mcp.json"), ("lsp", "lsp.json")):
        if kind not in SUPPORT[target]:
            continue
        paths = inventory["kinds"].get(kind, [])
        if paths:
            copy_path(source / paths[0], package / filename)
    for item in inventory["kinds"].get("instruction", []):
        copy_path(source / item, package / Path(item).name)


def render_notebooks(source: Path, package: Path, inventory: dict[str, Any]) -> None:
    for item in inventory["kinds"].get("jupyter-notebook", []):
        path = source if source.is_file() else source / item
        copy_path(path, package / "notebooks" / path.name)
    hosted = inventory["kinds"].get("hosted-notebook", [])
    if hosted:
        for item in hosted:
            copy_path(source / item, package / "notebook-import" / Path(item).name)
        (package / "notebook-import" / "IMPORT.md").write_text(
            "# Hosted notebook import\n\n"
            "No portable vendor import API was assumed. Recreate the notebook using the preserved sources, "
            "instructions, tools, conversation starters, sharing settings, and workflows in this directory. "
            "Verify permissions and sharing manually on the target platform.\n",
            encoding="utf-8",
        )


def render_manifest(source: Path, package: Path, inventory: dict[str, Any], target: str) -> None:
    name, version, description = manifest_identity(source, inventory)
    base = {"name": name, "version": version, "description": description}
    if target == "codex":
        base.update({
            "author": {"name": "Local developer"},
            "skills": "./skills/",
            "interface": {
                "displayName": " ".join(p.capitalize() for p in name.split("-")),
                "shortDescription": description[:64],
                "longDescription": description,
                "developerName": "Local developer",
                "category": "Productivity",
                "capabilities": ["Read", "Write"],
                "defaultPrompt": f"Use {name} for this task.",
            },
        })
        if (package / ".mcp.json").exists():
            base["mcpServers"] = "./.mcp.json"
        write_json(package / ".codex-plugin" / "plugin.json", base)
    elif target in {"claude", "grok"}:
        write_json(package / ".claude-plugin" / "plugin.json", base)
    elif target == "copilot":
        write_json(package / "plugin.json", base)
    elif target == "gemini":
        gemini = dict(base)
        if (package / ".mcp.json").exists():
            gemini["mcpServers"] = read_json(package / ".mcp.json")
            (package / ".mcp.json").unlink()
        write_json(package / "gemini-extension.json", gemini)


def render_package(source: Path, package: Path, inventory: dict[str, Any], target: str) -> None:
    package.mkdir(parents=True)
    copy_skills(source, package, inventory)
    if source.is_dir():
        render_commands(source, package, inventory, target)
        render_agents(source, package, inventory, target)
        render_hooks(source, package, inventory, target)
        copy_named_components(source, package, inventory, target)
    render_notebooks(source, package, inventory)
    render_manifest(source, package, inventory, target)


def yaml_list(values: Iterable[str]) -> str:
    return "[" + ", ".join(json.dumps(v) for v in values) + "]"


def write_job_okf(root: Path, inventory: dict[str, Any], plan: dict[str, Any], timestamp: str) -> None:
    root.mkdir(parents=True)
    (root / "index.md").write_text(
        '---\nokf_version: "0.1"\n---\n\n# Conversion job\n\n'
        '* [Source inventory](source.md) - immutable source facts and hashes\n'
        '* [Mapping](mapping.md) - target strategies and approximations\n'
        '* [Losses](losses.md) - unsupported behavior and follow-up work\n', encoding="utf-8")
    (root / "source.md").write_text(
        f'---\ntype: Source Inventory\ntitle: Source inventory\ndescription: Immutable inventory for this conversion.\n'
        f'tags: {yaml_list([inventory["platform"], "conversion-source"])}\ntimestamp: {timestamp}\n---\n\n'
        f'# Source\n\n`{inventory["source"]}`\n\n# Components\n\n```json\n{json.dumps(inventory["kinds"], indent=2)}\n```\n\n'
        'This inventory is mapped by the [conversion mapping](mapping.md).\n', encoding="utf-8")
    (root / "mapping.md").write_text(
        f'---\ntype: Conversion Mapping\ntitle: {inventory["platform"]} to {plan["target"]}\n'
        f'description: Exact and approximate mappings selected for the target.\ntags: {yaml_list([inventory["platform"], plan["target"], "mapping"])}\ntimestamp: {timestamp}\n---\n\n'
        f'# Mapping\n\n```json\n{json.dumps({"exact": plan["exact"], "approximations": plan["approximations"]}, indent=2)}\n```\n\n'
        'Review unsupported behavior in [losses](losses.md) and compare against the [source inventory](source.md).\n', encoding="utf-8")
    (root / "losses.md").write_text(
        f'---\ntype: Fidelity Report\ntitle: Conversion losses and follow-up\n'
        f'description: Unsupported features and manual actions for the rendered package.\ntags: {yaml_list([plan["target"], "fidelity"])}\ntimestamp: {timestamp}\n---\n\n'
        f'# Losses\n\n```json\n{json.dumps(plan["losses"], indent=2)}\n```\n\n'
        'These findings qualify the [mapping](mapping.md) derived from the [source inventory](source.md).\n', encoding="utf-8")
    (root / "log.md").write_text(
        f'# Conversion log\n\n## {timestamp[:10]}\n* **Creation**: Inventoried the source, selected mappings, rendered the target, and recorded fidelity findings.\n', encoding="utf-8")


def write_report(path: Path, inventory: dict[str, Any], plan: dict[str, Any]) -> None:
    def rows(items: list[dict[str, Any]], empty: str) -> str:
        return "\n".join(f"- **{i['kind']}**: {i.get('strategy') or i.get('reason')}" for i in items) or f"- {empty}"
    path.write_text(
        f"# AI Transmute conversion report\n\n"
        f"Source platform: `{inventory['platform']}`  \nTarget platform: `{plan['target']}`\n\n"
        f"## Exact mappings\n\n{rows(plan['exact'], 'None detected.')}\n\n"
        f"## Approximations\n\n{rows(plan['approximations'], 'None.')}\n\n"
        f"## Losses\n\n{rows(plan['losses'], 'None detected.')}\n\n"
        "## Manual follow-up\n\n"
        + ("Review every approximation and loss before installing the package.\n" if plan["manual_follow_up"] else "No mandatory manual follow-up detected; native validation is still recommended.\n"),
        encoding="utf-8",
    )


def validate_okf(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"available": bool(shutil.which("okf")), "valid": None}
    if not result["available"]:
        return result
    proc = subprocess.run(["okf", "validate", str(path), "--json"], capture_output=True, text=True, check=False)
    result.update({"exit_code": proc.returncode, "valid": proc.returncode == 0, "output": proc.stdout.strip() or proc.stderr.strip()})
    return result


def validate_target(path: Path, target: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    detected = target
    if (path / "job.json").is_file():
        job = read_json(path / "job.json")
        detected = target or str(job.get("target") or "")
        for required in ("package", "okf", "report.md", "job.json"):
            if not (path / required).exists():
                errors.append(f"missing job artifact: {required}")
        package = path / "package"
    else:
        package = path
    if detected == "codex" and not (package / ".codex-plugin" / "plugin.json").is_file():
        errors.append("missing .codex-plugin/plugin.json")
    elif detected in {"claude", "grok"} and not (package / ".claude-plugin" / "plugin.json").is_file():
        errors.append("missing .claude-plugin/plugin.json")
    elif detected == "copilot" and not (package / "plugin.json").is_file():
        errors.append("missing plugin.json")
    elif detected == "gemini" and not (package / "gemini-extension.json").is_file():
        errors.append("missing gemini-extension.json")
    for manifest in (package / ".codex-plugin" / "plugin.json", package / ".claude-plugin" / "plugin.json", package / "plugin.json", package / "gemini-extension.json"):
        if manifest.is_file():
            try:
                data = read_json(manifest)
                for key in ("name", "version", "description"):
                    if not data.get(key):
                        errors.append(f"{manifest}: missing {key}")
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(str(exc))
    okf_result = validate_okf(path / "okf") if (path / "okf").is_dir() else None
    if okf_result and okf_result.get("valid") is False:
        errors.append("job OKF bundle is invalid")
    return {"path": str(path), "target": detected, "valid": not errors, "errors": errors, "okf": okf_result}


def convert(source_arg: str, target: str, output: str | None) -> dict[str, Any]:
    inventory = inspect_source(source_arg)
    source = Path(inventory["source"])
    plan = plan_conversion(inventory, target)
    parent = Path(output).expanduser().resolve() if output else Path.cwd() / "ai-transmute"
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    job_root = parent / f"{stamp}-{source_name(source)}-to-{target}"
    if job_root.exists():
        raise FileExistsError(f"refusing to overwrite {job_root}")
    job_root.mkdir(parents=True)
    render_package(source, job_root / "package", inventory, target)
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    write_job_okf(job_root / "okf", inventory, plan, timestamp)
    write_report(job_root / "report.md", inventory, plan)
    job = {
        "schema_version": 1,
        "operation": "convert",
        "created_at": timestamp,
        "source": inventory["source"],
        "source_platform": inventory["platform"],
        "target": target,
        "artifact_kinds": sorted(inventory["kinds"]),
        "status": "rendered",
        "paths": {"package": "package", "okf": "okf", "report": "report.md"},
        "approximations": plan["approximations"],
        "losses": plan["losses"],
    }
    write_json(job_root / "job.json", job)
    validation = validate_target(job_root, target)
    job["status"] = "validated" if validation["valid"] else "rendered-with-validation-errors"
    job["validation"] = validation
    write_json(job_root / "job.json", job)
    return {"job": str(job_root), "plan": plan, "validation": validation}


def extract(source_arg: str, selected: str, output: str | None) -> dict[str, Any]:
    inventory = inspect_source(source_arg)
    source = Path(inventory["source"])
    kinds = [k.strip() for k in selected.split(",") if k.strip()]
    unknown = sorted(set(kinds) - set(KINDS))
    if unknown:
        raise ValueError(f"unknown kinds: {', '.join(unknown)}")
    parent = Path(output).expanduser().resolve() if output else Path.cwd() / "ai-transmute-extract"
    destination = parent / f"{source_name(source)}-assets"
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    destination.mkdir(parents=True)
    copied = []
    for kind in kinds:
        for item in inventory["kinds"].get(kind, []):
            path = source if source.is_file() else source / item
            target = destination / kind / (path.name if source.is_file() else item)
            copy_path(path, target)
            copied.append({"kind": kind, "source": str(path), "target": str(target)})
    write_json(destination / "extraction.json", {"source": inventory["source"], "selected": kinds, "copied": copied})
    return {"output": str(destination), "copied": copied}


def diff_artifacts(left: str, right: str) -> dict[str, Any]:
    a, b = inspect_source(left), inspect_source(right)
    a_kinds, b_kinds = set(a["kinds"]), set(b["kinds"])
    return {
        "left_platform": a["platform"], "right_platform": b["platform"],
        "shared_kinds": sorted(a_kinds & b_kinds),
        "missing_on_right": sorted(a_kinds - b_kinds),
        "added_on_right": sorted(b_kinds - a_kinds),
        "file_count": {"left": a["file_count"], "right": b["file_count"]},
        "notebook_cells": {
            "left": sum(n.get("cells", 0) for n in a["notebooks"]),
            "right": sum(n.get("cells", 0) for n in b["notebooks"]),
        },
    }


def doctor() -> dict[str, Any]:
    tools = {name: shutil.which(name) for name in ("python3", "okf", "ruby", "codex", "claude", "copilot", "grok", "gemini")}
    return {
        "tools": tools,
        "required_ready": bool(tools["python3"] and tools["okf"]),
        "native_validators": {name: bool(tools[name]) for name in TARGETS},
        "python": sys.version.split()[0],
    }


def emit(value: Any, as_json: bool = False) -> None:
    if as_json or isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(value)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Convert AI extension artifacts through auditable OKF jobs.")
    sub = root.add_subparsers(dest="command", required=True)
    inspect_p = sub.add_parser("inspect")
    inspect_p.add_argument("source")
    inspect_p.add_argument("--json", action="store_true")
    plan_p = sub.add_parser("plan")
    plan_p.add_argument("source")
    plan_p.add_argument("--target", choices=TARGETS, required=True)
    plan_p.add_argument("--json", action="store_true")
    convert_p = sub.add_parser("convert")
    convert_p.add_argument("source")
    convert_p.add_argument("--target", choices=TARGETS, required=True)
    convert_p.add_argument("--output")
    convert_p.add_argument("--json", action="store_true")
    extract_p = sub.add_parser("extract")
    extract_p.add_argument("source")
    extract_p.add_argument("--select", required=True)
    extract_p.add_argument("--output")
    extract_p.add_argument("--json", action="store_true")
    validate_p = sub.add_parser("validate")
    validate_p.add_argument("path")
    validate_p.add_argument("--target", choices=TARGETS)
    validate_p.add_argument("--json", action="store_true")
    diff_p = sub.add_parser("diff")
    diff_p.add_argument("left")
    diff_p.add_argument("right")
    diff_p.add_argument("--json", action="store_true")
    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "inspect":
            result = inspect_source(args.source)
        elif args.command == "plan":
            result = plan_conversion(inspect_source(args.source), args.target)
        elif args.command == "convert":
            result = convert(args.source, args.target, args.output)
        elif args.command == "extract":
            result = extract(args.source, args.select, args.output)
        elif args.command == "validate":
            result = validate_target(Path(args.path).expanduser().resolve(), args.target)
        elif args.command == "diff":
            result = diff_artifacts(args.left, args.right)
        else:
            result = doctor()
        emit(result, getattr(args, "json", False))
        return 0 if not isinstance(result, dict) or result.get("valid", True) else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
