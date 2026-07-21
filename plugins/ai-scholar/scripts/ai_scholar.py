#!/usr/bin/env python3
"""Deterministic state and quality gates for AI Scholar research jobs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1"
STATES = (
    "initialized", "sourcing", "triaged", "curated", "design-draft", "review",
    "approved", "implemented", "validated", "handoff-ready", "rejected",
)
TRANSITIONS = {
    "initialized": {"sourcing"},
    "sourcing": {"triaged"},
    "triaged": {"curated"},
    "curated": {"design-draft"},
    "design-draft": {"review"},
    "review": {"design-draft", "rejected"},
    "approved": {"implemented"},
    "implemented": {"validated"},
    "validated": {"handoff-ready"},
    "handoff-ready": set(),
    "rejected": {"design-draft"},
}
REQUIRED_FILES = (
    "sources/registry.md", "sources/discarded.md", "sources/special-cases.md",
    "sources/conflicts.md", "sources/uncertainties.md", "knowledge/index.md",
    "knowledge/log.md", "design/interface.md", "design/approval.md", "report.md",
)


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result[:48] or "research-job"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_job(path: str) -> tuple[Path, dict[str, Any]]:
    root = Path(path).resolve()
    job_file = root / "job.json"
    if not job_file.is_file():
        raise ValueError(f"No AI Scholar job.json at {root}")
    try:
        job = json.loads(job_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid job.json: {exc}") from exc
    return root, job


def save_job(root: Path, job: dict[str, Any]) -> None:
    job["updated_at"] = now()
    write_json(root / "job.json", job)


def markdown(title: str, body: str) -> str:
    return f"# {title}\n\n{body.rstrip()}\n"


def init_job(topic: str, output: str, goal: str, audience: str) -> dict[str, Any]:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    root = Path(output).resolve() / f"{stamp}-{slug(topic)}"
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite existing job: {root}")
    for relative in ("sources", "knowledge", "design", "package"):
        (root / relative).mkdir(parents=True, exist_ok=True)
    created = now()
    job = {
        "schema_version": SCHEMA_VERSION,
        "job_id": root.name,
        "topic": topic,
        "goal": goal,
        "audience": audience,
        "state": "initialized",
        "created_at": created,
        "updated_at": created,
        "review": {"decision": "pending", "reviewer": None, "decided_at": None},
        "phase_history": [{"state": "initialized", "at": created, "note": "Job created."}],
    }
    write_json(root / "job.json", job)
    (root / "sources" / "registry.md").write_text(markdown("Source registry", "Use one entry per candidate source, recording canonical URL, publisher, source class, claims covered, authority/relevance/uniqueness rationale, duplicate group, disposition, and access date."), encoding="utf-8")
    (root / "sources" / "discarded.md").write_text(markdown("Deferred and discarded sources", "Keep every excluded or deferred source here with its canonical URL and the reason it was not retained."), encoding="utf-8")
    (root / "sources" / "special-cases.md").write_text(markdown("Special cases", "Record exceptions, edge cases, and targeted follow-up research here."), encoding="utf-8")
    (root / "sources" / "conflicts.md").write_text(markdown("Conflict ledger", "Record conflicting claims, their sources, resolution status, and the evidence needed to resolve them."), encoding="utf-8")
    (root / "sources" / "uncertainties.md").write_text(markdown("Uncertainty ledger", "Record unverified, incomplete, or inference-only conclusions. Do not present them as sourced facts."), encoding="utf-8")
    (root / "knowledge" / "index.md").write_text("---\nokf_version: \"0.1\"\n---\n\n# Research knowledge\n\nCurated knowledge for this research job.\n", encoding="utf-8")
    (root / "knowledge" / "log.md").write_text(f"# Research knowledge log\n\n## {created[:10]}\n* **Creation**: Initialized research bundle for {topic}.\n", encoding="utf-8")
    (root / "design" / "interface.md").write_text(markdown("Plugin interface design", "Pending curated research. The final design must trace each public capability to a cited requirement or a clearly labeled design decision."), encoding="utf-8")
    (root / "design" / "approval.md").write_text(markdown("Design approval", "Status: pending\n\nImplementation and marketplace edits are prohibited until the user explicitly approves the design."), encoding="utf-8")
    (root / "report.md").write_text(markdown("AI Scholar job report", "Status: initialized\n\nThis report will summarize source coverage, curation, design traceability, review, implementation, and validation."), encoding="utf-8")
    return {"job": str(root), "state": job["state"], "valid": True}


def transition(root: Path, job: dict[str, Any], target: str, note: str) -> dict[str, Any]:
    current = job.get("state")
    if target not in STATES:
        raise ValueError(f"Unknown state: {target}")
    if target == "approved":
        raise ValueError("Use record-review --decision approved for the approval transition.")
    if target not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Cannot transition from {current} to {target}")
    job["state"] = target
    job.setdefault("phase_history", []).append({"state": target, "at": now(), "note": note})
    save_job(root, job)
    return {"job": str(root), "state": target, "valid": True}


def record_review(root: Path, job: dict[str, Any], decision: str, reviewer: str, notes: str) -> dict[str, Any]:
    if job.get("state") not in {"design-draft", "review"}:
        raise ValueError("A review can only be recorded from design-draft or review state.")
    timestamp = now()
    if decision == "approved":
        new_state = "approved"
    elif decision == "changes-requested":
        new_state = "design-draft"
    else:
        new_state = "rejected"
    job["state"] = new_state
    job["review"] = {"decision": decision, "reviewer": reviewer, "decided_at": timestamp}
    job.setdefault("phase_history", []).append({"state": new_state, "at": timestamp, "note": f"Review decision: {decision}."})
    (root / "design" / "approval.md").write_text(markdown("Design approval", f"Status: {decision}\nReviewer: {reviewer}\nDecided at: {timestamp}\n\n## Notes\n\n{notes or 'No additional notes provided.'}"), encoding="utf-8")
    save_job(root, job)
    return {"job": str(root), "state": new_state, "review": job["review"], "valid": True}


def verify(root: Path, job: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for key in ("schema_version", "job_id", "topic", "goal", "audience", "state", "review", "phase_history"):
        if not job.get(key):
            errors.append(f"job.json is missing {key}")
    if job.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Unsupported schema version: {job.get('schema_version')}")
    if job.get("state") not in STATES:
        errors.append(f"Unknown job state: {job.get('state')}")
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"Missing required artifact: {relative}")
    knowledge_index = root / "knowledge" / "index.md"
    if knowledge_index.is_file() and "okf_version" not in knowledge_index.read_text(encoding="utf-8")[:128]:
        errors.append("knowledge/index.md is not an OKF bundle root")
    review = job.get("review") or {}
    if job.get("state") == "approved" and review.get("decision") != "approved":
        errors.append("Approved state lacks an explicit approved review decision")
    if review.get("decision") == "approved" and job.get("state") not in {"approved", "implemented", "validated", "handoff-ready"}:
        errors.append("Approved review decision has an inconsistent job state")
    return {"job": str(root), "state": job.get("state"), "valid": not errors, "errors": errors}


def gate(root: Path, job: dict[str, Any], action: str) -> dict[str, Any]:
    result = verify(root, job)
    errors = list(result["errors"])
    state = job.get("state")
    if action == "implement":
        if state != "approved" or (job.get("review") or {}).get("decision") != "approved":
            errors.append("Implementation requires an explicitly approved design review.")
    elif action == "handoff":
        if state != "validated":
            errors.append("Handoff requires validated state.")
    else:
        raise ValueError(f"Unknown gate action: {action}")
    return {"job": str(root), "action": action, "state": state, "valid": not errors, "errors": errors}


def emit(value: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2))
    elif value.get("valid", True):
        print(f"{value.get('job', '')}: {value.get('state', 'ok')}")
    else:
        print("\n".join(value.get("errors", [])), file=sys.stderr)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Manage auditable AI Scholar research jobs.")
    sub = root.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("topic")
    init.add_argument("--output", default=".")
    init.add_argument("--goal", default="Design a high-quality Codex plugin grounded in curated knowledge.")
    init.add_argument("--audience", default="Codex users")
    init.add_argument("--json", action="store_true")
    status = sub.add_parser("status")
    status.add_argument("job")
    status.add_argument("--json", action="store_true")
    advance = sub.add_parser("advance")
    advance.add_argument("job")
    advance.add_argument("--to", required=True)
    advance.add_argument("--note", default="")
    advance.add_argument("--json", action="store_true")
    review = sub.add_parser("record-review")
    review.add_argument("job")
    review.add_argument("--decision", choices=("approved", "changes-requested", "rejected"), required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", default="")
    review.add_argument("--json", action="store_true")
    verify_p = sub.add_parser("verify")
    verify_p.add_argument("job")
    verify_p.add_argument("--json", action="store_true")
    gate_p = sub.add_parser("gate")
    gate_p.add_argument("job")
    gate_p.add_argument("action", choices=("implement", "handoff"))
    gate_p.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "init":
            result = init_job(args.topic, args.output, args.goal, args.audience)
        else:
            job_root, job = read_job(args.job)
            if args.command == "status":
                result = {"job": str(job_root), "state": job.get("state"), "review": job.get("review"), "valid": True}
            elif args.command == "advance":
                result = transition(job_root, job, args.to, args.note)
            elif args.command == "record-review":
                result = record_review(job_root, job, args.decision, args.reviewer, args.notes)
            elif args.command == "verify":
                result = verify(job_root, job)
            else:
                result = gate(job_root, job, args.action)
        emit(result, args.json)
        return 0 if result.get("valid", True) else 2
    except (OSError, ValueError, FileExistsError) as exc:
        result = {"valid": False, "errors": [str(exc)]}
        emit(result, getattr(args, "json", False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
