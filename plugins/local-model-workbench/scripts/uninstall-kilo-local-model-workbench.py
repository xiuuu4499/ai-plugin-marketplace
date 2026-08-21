#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path


def kilo_config_root() -> Path:
    override = os.environ.get("KILO_TARGET_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config).expanduser() / "kilo"
    return Path.home() / ".config" / "kilo"


def remove_empty_dirs(paths: list[Path], config_root: Path) -> None:
    for path in paths:
        try:
            resolved = path.resolve()
            root = config_root.resolve()
            if root not in [resolved, *resolved.parents]:
                continue
            while resolved != root and resolved.exists():
                resolved.rmdir()
                resolved = resolved.parent
        except OSError:
            continue


def main() -> int:
    config_root = kilo_config_root()
    manifest = config_root / ".local-model-workbench.manifest"
    if not manifest.is_file():
        print(f"No local-model-workbench manifest found in {config_root}")
        return 0

    root = config_root.resolve()
    removed_parents: list[Path] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        target = Path(line).expanduser()
        try:
            resolved = target.resolve()
        except OSError:
            resolved = target.absolute()
        if root not in [resolved, *resolved.parents]:
            print(f"skip unsafe manifest path: {target}")
            continue
        if target.is_file():
            target.unlink()
            removed_parents.append(target.parent)
            print(f"removed {target}")

    manifest.unlink(missing_ok=True)
    remove_empty_dirs(
        [
            config_root / "skills" / "local-model-workbench",
            config_root / "agents",
            *removed_parents,
        ],
        config_root,
    )
    print(f"Uninstalled Local Model Workbench Kilo artifacts from {config_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
