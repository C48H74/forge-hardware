"""Packaging and isolated skill-install tests; no CAD kernel or host app required."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExtensionsTest(unittest.TestCase):
    def test_manifests_are_current_and_references_exist(self):
        builder = load_script("build_extensions")
        for path, expected in builder.manifests().items():
            with self.subTest(path=path):
                actual = json.loads((ROOT / path).read_text())
                self.assertEqual(actual, expected)
                if "skills" in actual:
                    self.assertTrue((ROOT / actual["skills"] / "forge-hardware/SKILL.md").is_file())
                self.assertNotIn("mcpServers", actual)

    def test_every_agent_receives_complete_skill_and_preserves_existing(self):
        installer = load_script("install_agent_skill")
        source = ROOT / "skills/forge-hardware"
        with tempfile.TemporaryDirectory() as temp:
            for agent in installer.AGENTS:
                with self.subTest(agent=agent):
                    base = Path(temp) / agent
                    target = installer.install(agent, base, dry_run=True)
                    self.assertFalse(base.exists())
                    self.assertEqual(installer.install(agent, base), target)
                    for path in source.rglob("*"):
                        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                            self.assertEqual(path.read_bytes(), (target / path.relative_to(source)).read_bytes())
                    sentinel = target / "local-notes.txt"
                    sentinel.write_text("keep")
                    with self.assertRaises(FileExistsError):
                        installer.install(agent, base)
                    self.assertEqual(sentinel.read_text(), "keep")

    def test_dangling_symlink_is_not_overwritten(self):
        installer = load_script("install_agent_skill")
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / installer.AGENTS["codex"] / "forge-hardware"
            target.parent.mkdir(parents=True)
            target.symlink_to(Path(temp) / "missing", target_is_directory=True)
            with self.assertRaises(FileExistsError):
                installer.install("codex", temp)
            self.assertTrue(target.is_symlink())


if __name__ == "__main__":
    unittest.main()
