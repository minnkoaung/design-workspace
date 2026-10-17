import hashlib
import json
import os
from provider_fixtures import CATALOG, FAKE
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="design-team-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace with spaces"
        self.root.mkdir()
        for name in (".agents", "skills", "docs", "standards", "templates", "scripts", "tests"):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("README.md", "AGENTS.md", "CLAUDE.md", "BOOTSTRAP.md", ".gitignore", "design-workspace"):
            shutil.copy2(ROOT / name, self.root / name)

    def call(self, *args, root=None, success=True, input_text=None):
        target = root or self.root
        binary = self.root / 'fixture-bin/codex'
        binary.parent.mkdir(exist_ok=True)
        binary.write_text(FAKE)
        binary.chmod(0o755)
        environment = dict(os.environ)
        environment['PATH'] = str(binary.parent) + os.pathsep + environment.get('PATH', '')
        environment['FIXTURE_MODELS'] = json.dumps([{'model': m['model'], 'supportedReasoningEfforts': [{'reasoningEffort': e} for e in m['efforts']], 'defaultReasoningEffort': m['default_effort'], 'inputModalities': m['modalities']} for m in CATALOG['models']])
        if args and args[0] == 'init' and not (target / 'workspace.local.json').exists():
            settings = {'model_routing': {'version': 1, 'provider': 'codex', 'mode': 'balanced',
                        'tiers': {tier: {'model': m['model'], 'effort': m['default_effort']} for tier,m in zip(('light','standard','strong'),CATALOG['models'])},
                        'max_attempts': 1, 'max_context_chars': 30000, 'timeout_seconds': 30, 'catalog': CATALOG}}
            (target / 'workspace.local.json').write_text(json.dumps(settings))
        result = subprocess.run([sys.executable, str(target / "scripts/workspace.py"), *args],
                                text=True, capture_output=True, cwd=self.temp.name, input=input_text, env=environment)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def new(self, slug="alpha"):
        self.call("new", slug, "--name", "Alpha Project")
        return self.root / "features" / slug

    def test_init_new_captures_multiline_requirements_and_preserves_gates(self):
        result = self.call("init", input_text="invalid\nNEW\nCustomer Portal\n\n.\nManage portal users.\nReference: /tmp/source with spaces.md\n.\nWeb\nSeven main screens\n")
        self.assertIn("New project / feature", result.stdout)
        self.assertIn("Enter requirements or a source path", result.stdout)
        run = self.root / "features/customer-portal"
        intake = json.loads((run / "requirements/intake.json").read_text())
        self.assertEqual(intake["requirements"], "Manage portal users.\nReference: /tmp/source with spaces.md")
        self.assertEqual(intake["target_surface"], "Web")
        self.assertEqual(intake["desired_deliverables"], "Seven main screens")
        data = json.loads((run / "checkpoint.json").read_text())
        self.assertEqual(data["stage"], 0)
        self.assertFalse(data["final_output_accepted"])
        self.assertEqual(data["gates"]["A_B"], "pending")
        self.assertIn("intake.json", data["next_action"])
        self.assertIn("sources not yet inspected", (run / "status.md").read_text())
        self.assertIn("Resume feature customer-portal", result.stdout)
        self.call("check", "customer-portal")

    def test_init_resume_selection_and_exit_do_not_mutate_feature(self):
        run = self.new()
        before = {p: p.read_bytes() for p in run.rglob("*") if p.is_file()}
        result = self.call("init", input_text="resume\nwrong\n1\n")
        self.assertIn("1. alpha | ready | stage 0", result.stdout)
        self.assertIn("Resume feature alpha", result.stdout)
        self.assertIn("Resume feature alpha", self.call("init", input_text="2\nalpha\n").stdout)
        self.call("init", input_text="0\n")
        self.call("init", input_text="2\n0\n")
        self.assertEqual(before, {p: p.read_bytes() for p in run.rglob("*") if p.is_file()})

    def test_init_cancel_empty_resume_and_duplicate_id(self):
        self.assertIn("No saved features", self.call("init", input_text="2\n").stdout)
        self.assertIn("Cancelled", self.call("init", input_text="1\nUnfinished\n\nSome requirements\n").stdout)
        self.assertFalse((self.root / "features").exists())
        self.new()
        result = self.call("init", input_text="1\nAnother\nalpha\n../escape\nbeta\nBrief\n.\n\n\n")
        self.assertIn("already exists", result.stdout)
        self.assertIn("lowercase words", result.stdout)
        self.call("check", "alpha")
        self.call("check", "beta")

    def test_doctor_new_duplicate_and_traversal(self):
        self.assertIn("PASS", self.call("doctor").stdout)
        run = self.new()
        before = (run / "status.md").read_bytes()
        self.call("check", "alpha")
        self.call("new", "alpha", success=False)
        self.assertEqual(before, (run / "status.md").read_bytes())
        self.call("new", "../escape", success=False)
        self.assertFalse((self.root / "escape").exists())
        self.assertIn("stage 0", self.call("list").stdout)
        self.assertIn("Resume feature alpha", self.call("resume", "alpha").stdout)

    def test_hash_change_and_refresh_without_implying_approval(self):
        run = self.new()
        status = run / "status.md"
        status.write_text(status.read_text() + "\nIntake note: source requested.\n")
        self.assertIn("Changed since checkpoint", self.call("check", "alpha", success=False).stdout)
        self.call("checkpoint", "alpha")
        self.call("check", "alpha")
        data = json.loads((run / "checkpoint.json").read_text())
        self.assertEqual(data["stage"], 0)
        self.assertFalse(data["final_output_accepted"])
        self.assertEqual(data["gates"]["A_B"], "pending")

    def test_routed_task_plan_requires_config_and_keeps_checkpoint(self):
        run = self.new()
        before = (run / "checkpoint.json").read_bytes()
        self.assertIn("not configured", self.call("models", "status", success=False).stderr)
        self.call("task", "plan", "alpha", "requirements", success=False)
        settings = {"model_routing": {"version": 1, "provider": "codex", "mode": "balanced",
                    "tiers": {tier: {"model": "fixture-" + tier, "effort": None} for tier in ("light", "standard", "strong")},
                    "max_attempts": 1, "max_context_chars": 30000, "timeout_seconds": 30}}
        (self.root / "workspace.local.json").write_text(json.dumps(settings))
        self.assertIn('"model": "fixture-standard"', self.call("task", "plan", "alpha", "requirements").stdout)
        self.assertEqual(before, (run / "checkpoint.json").read_bytes())
        self.assertFalse((run / "history/agent-runs").exists())

    def test_source_drift_is_not_silently_rebaselined(self):
        run = self.new()
        source = run / "sources" / "brief.md"
        source.parent.mkdir()
        source.write_text("Approved evidence\n")
        item = {"path": source.relative_to(self.root).as_posix(), "bytes": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        cp = run / "checkpoint.json"
        data = json.loads(cp.read_text())
        data["local_source_baseline"] = [item]
        cp.write_text(json.dumps(data))
        before = cp.read_bytes()
        source.write_text("Unapproved replacement\n")
        self.call("checkpoint", "alpha", success=False)
        self.assertEqual(cp.read_bytes(), before)
        self.call("check", "alpha", success=False)

    def test_escape_record_is_rejected(self):
        run = self.new()
        cp = run / "checkpoint.json"
        data = json.loads(cp.read_text())
        data["artifacts"][0]["path"] = "../outside.md"
        cp.write_text(json.dumps(data))
        self.assertIn("escapes", self.call("check", "alpha", success=False).stdout)

    @unittest.skipIf(sys.platform == "win32", "Symlink fixture requires native privileges")
    def test_new_refuses_symlinked_output_directories(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "features").symlink_to(outside, target_is_directory=True)
        self.call("new", "escaped", success=False)
        self.assertFalse((outside / "escaped").exists())
        (self.root / "features").unlink()
        (self.root / "WIP").symlink_to(outside, target_is_directory=True)
        self.call("new", "escaped", success=False)
        self.assertFalse((self.root / "features/escaped").exists())

    def test_clean_starter_excludes_projects_and_credentials(self):
        self.new()
        (self.root / ".env").write_text("EXAMPLE_DO_NOT_SHARE=fixture-only")
        (self.root / ".aws").mkdir()
        (self.root / ".aws/credentials").write_text("fixture only")
        (self.root / "docs/auth.json").write_text("fixture only")
        (self.root / "workspace.local.json").write_text('{"model_routing": "fixture only"}')
        (self.root / "docs/workspace.local.json.tmp").write_text('fixture only')
        output = Path(self.temp.name) / "starter.zip"
        self.call("pack", "--output", str(output))
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertTrue(any(n.endswith("scripts/workspace.py") for n in names))
            self.assertTrue(any(n.endswith(".agents/skills/design-workflow/SKILL.md") for n in names))
            self.assertTrue(any(n.endswith("skills/ui-ux-design-review/SKILL.md") for n in names))
            self.assertFalse(any("/features/" in n or "/WIP/" in n for n in names))
            self.assertFalse(any(n.endswith(".env") or "/.aws/" in n or n.endswith("auth.json") for n in names))
            self.assertFalse(any(n.endswith("workspace.local.json") or n.endswith("workspace.local.json.tmp") for n in names))
            self.assertFalse(any("ctzpay-prd-to-drd/" in n for n in names))
            self.assertFalse(any(n.endswith("/docs/workspace-plan.md") or n.endswith("/docs/skill-provenance.md") for n in names))
            destination = Path(self.temp.name) / "recipient"
            archive.extractall(destination)
        receiver = destination / "design-workspace"
        self.call("doctor", root=receiver)
        self.call("list", root=receiver)
        self.call("pack", "--output", str(output), success=False)

    def test_selected_project_survives_relocation(self):
        self.new("alpha")
        self.new("beta")
        output = Path(self.temp.name) / "project.zip"
        self.call("pack", "--include-feature", "alpha", "--output", str(output))
        destination = Path(self.temp.name) / "another teammate" / "checkout"
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertTrue(any("/features/alpha/" in n for n in names))
            self.assertFalse(any("/features/beta/" in n for n in names))
            archive.extractall(destination)
        receiver = destination / "design-workspace"
        self.call("check", "alpha", root=receiver)
        self.call("resume", "alpha", root=receiver)
        self.assertFalse((receiver / "features/beta").exists())

    @unittest.skipIf(sys.platform == "win32", "POSIX launcher; Windows uses Python entry point")
    def test_launcher_works_outside_checkout(self):
        launcher = self.root / "design-workspace"
        launcher.chmod(0o755)
        result = subprocess.run([str(launcher), "doctor"], cwd=self.temp.name,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
