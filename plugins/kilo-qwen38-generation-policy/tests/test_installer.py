import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install-kilo-qwen38-policy.sh"
INSTALL_PY = ROOT / "scripts" / "install-kilo-qwen38-policy.py"
UNINSTALL = ROOT / "scripts" / "uninstall-kilo-qwen38-policy.sh"
UNINSTALL_PY = ROOT / "scripts" / "uninstall-kilo-qwen38-policy.py"


class InstallerTests(unittest.TestCase):
    def test_install_idempotent_and_uninstall_owned_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "kilo"
            unrelated = target / "kilo.jsonc"
            target.mkdir(parents=True)
            unrelated.write_text("// keep me\n{}", encoding="utf-8")
            env = {**os.environ, "KILO_TARGET_CONFIG_DIR": target.as_posix()}

            subprocess.run(["python3", INSTALL_PY.as_posix()], check=True, env=env, cwd="/tmp", capture_output=True, text=True)
            subprocess.run([INSTALL.as_posix()], check=True, env=env, cwd=ROOT.as_posix(), capture_output=True, text=True)

            self.assertTrue((target / "plugin" / "qwen38-generation-policy.js").is_file())
            self.assertTrue((target / "agents" / "chat.md").is_file())
            self.assertTrue((target / "skills" / "qwen38-generation-policy" / "SKILL.md").is_file())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "// keep me\n{}")

            subprocess.run([UNINSTALL.as_posix()], check=True, env=env, cwd="/tmp", capture_output=True, text=True)
            self.assertFalse((target / "plugin" / "qwen38-generation-policy.js").exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "// keep me\n{}")

            subprocess.run(["python3", UNINSTALL_PY.as_posix()], check=True, env=env, cwd="/tmp", capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
