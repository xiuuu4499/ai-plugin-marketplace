import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install-kilo-local-model-workbench.sh"
INSTALL_PY = ROOT / "scripts" / "install-kilo-local-model-workbench.py"
UNINSTALL = ROOT / "scripts" / "uninstall-kilo-local-model-workbench.sh"
UNINSTALL_PY = ROOT / "scripts" / "uninstall-kilo-local-model-workbench.py"
CHECK = ROOT / "scripts" / "local-model-workbench-check.py"


class LocalModelWorkbenchScriptTests(unittest.TestCase):
    def test_install_idempotent_and_uninstall_owned_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "kilo"
            unrelated = target / "kilo.jsonc"
            target.mkdir(parents=True)
            unrelated.write_text("// keep me\n{}", encoding="utf-8")
            env = {**os.environ, "KILO_TARGET_CONFIG_DIR": target.as_posix()}

            subprocess.run(["python3", INSTALL_PY.as_posix()], check=True, env=env, cwd="/tmp", capture_output=True, text=True)
            subprocess.run([INSTALL.as_posix()], check=True, env=env, cwd=ROOT.as_posix(), capture_output=True, text=True)

            self.assertTrue((target / "agents" / "local-model-workbench.md").is_file())
            self.assertTrue((target / "skills" / "local-model-workbench" / "SKILL.md").is_file())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "// keep me\n{}")

            subprocess.run([UNINSTALL.as_posix()], check=True, env=env, cwd="/tmp", capture_output=True, text=True)
            self.assertFalse((target / "agents" / "local-model-workbench.md").exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "// keep me\n{}")

            subprocess.run(["python3", UNINSTALL_PY.as_posix()], check=True, env=env, cwd="/tmp", capture_output=True, text=True)

    def test_environment_check_runs(self):
        result = subprocess.run(["python3", CHECK.as_posix()], check=True, capture_output=True, text=True)
        self.assertIn("Local model workbench environment check", result.stdout)


if __name__ == "__main__":
    unittest.main()
