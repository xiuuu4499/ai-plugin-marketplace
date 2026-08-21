#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from pathlib import Path


def kilo_config_root() -> Path:
    override = os.environ.get("KILO_TARGET_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config).expanduser() / "kilo"
    return Path.home() / ".config" / "kilo"


def install_file(source: Path, target: Path, manifest_lines: list[str]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    target.chmod(0o644)
    manifest_lines.append(str(target))


def install_tree_files(source_dir: Path, target_dir: Path, manifest_lines: list[str]) -> None:
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        install_file(source, target_dir / source.relative_to(source_dir), manifest_lines)


def main() -> int:
    plugin_root = Path(__file__).resolve().parents[1]
    config_root = kilo_config_root()
    manifest = config_root / ".local-model-workbench.manifest"
    manifest_lines: list[str] = []

    (config_root / "agents").mkdir(parents=True, exist_ok=True)
    (config_root / "skills").mkdir(parents=True, exist_ok=True)

    install_tree_files(plugin_root / "kilo" / "agents", config_root / "agents", manifest_lines)
    install_tree_files(
        plugin_root / "skills" / "local-model-workbench",
        config_root / "skills" / "local-model-workbench",
        manifest_lines,
    )

    manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"Installed Local Model Workbench Kilo artifacts into {config_root}")
    print("Run /reload in Kilo or restart Kilo to load updated agents and skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
