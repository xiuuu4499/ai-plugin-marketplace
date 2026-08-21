#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


def check_cmd(name: str) -> None:
    found = shutil.which(name)
    if found:
        print(f"ok: {name} ({found})")
    else:
        print(f"missing: {name}")


def main() -> int:
    home = Path.home()
    print("Local model workbench environment check")
    for command in ["kilo", "llama-server", "llama-swap", "node", "npm", "python3"]:
        check_cmd(command)

    kilo_config = home / ".config" / "kilo"
    if kilo_config.is_dir():
        print(f"ok: Kilo config directory exists at {kilo_config}")
    else:
        print(f"missing: Kilo config directory at {kilo_config}")

    comfyui = home / "ComfyUI"
    if comfyui.is_dir():
        print(f"ok: ComfyUI directory exists at {comfyui}")
    else:
        print(f"note: ComfyUI directory not found at {comfyui}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
