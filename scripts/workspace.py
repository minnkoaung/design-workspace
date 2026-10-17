#!/usr/bin/env python3
"""Portable local design-workspace helpers. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile
import model_router
import agent_runtime

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", "BOOTSTRAP.md", ".gitignore", "design-workspace")
RUNTIME_DIRS = (".agents", "skills", "docs", "standards", "templates", "scripts", "tests")
LOCAL_ONLY_PATHS = (".agents/skills/ctzpay-prd-to-drd", "docs/workspace-plan.md",
                    "docs/setup-validation.md", "docs/team-cli-validation.md", "docs/skill-provenance.md")
REQUIRED = ("AGENTS.md", "BOOTSTRAP.md", "templates/status.md", "templates/wip-entry.md",
            "scripts/model_router.py", "scripts/agent_runtime.py", "scripts/providers/__init__.py",
            "standards/review-checklist.md", ".agents/skills/design-workflow/SKILL.md",
            ".agents/skills/design-workflow/references/stages.md",
            ".agents/skills/design-workflow/references/recovery.md",
            "skills/ui-ux-design-review/SKILL.md")


def contained(path: Path, root: Path) -> bool:
    return path.resolve().is_relative_to(root.resolve())


def feature(root: Path, slug: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Feature ID must use lowercase words separated by hyphens.")
    target = root / "features" / slug
    if (not contained(target, root) or not contained(target, root / "features")
            or (root / "features").is_symlink() or target.is_symlink()):
        raise ValueError("Feature path must stay inside features/ without a symlink.")
    return target


def read_checkpoint(run: Path) -> dict:
    data = json.loads((run / "checkpoint.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Checkpoint must be a JSON object.")
    return data


def record(root: Path, path: Path) -> dict:
    if path.is_symlink() or not contained(path, root):
        raise ValueError(f"Cannot register a path outside the workspace: {path}")
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def resolve_record(root: Path, item: dict, data: dict) -> Path:
    path = Path(item["path"])
    if path.is_absolute():
        if data.get("schema_version", 1) >= 3:
            raise ValueError(f"Required checkpoint path is not portable: {path}")
        resolved = path
    else:
        resolved = root / path
    if not contained(resolved, root) or resolved.is_symlink():
        raise ValueError(f"Required checkpoint path escapes the workspace: {path}")
    return resolved


def check_feature(root: Path, slug: str) -> list[str]:
    run = feature(root, slug)
    data = read_checkpoint(run)
    errors = []
    if data.get("feature_id") != slug:
        errors.append("Checkpoint feature ID does not match its folder.")
    if data.get("schema_version", 1) >= 3 and data.get("path_base") != "workspace":
        errors.append("Schema 3 checkpoints must declare path_base=workspace.")
    required = ("status.md", "decisions.md", "RESUME.md")
    for name in required:
        if not (run / name).is_file():
            errors.append(f"Missing coordination file: {name}")
    records = data.get("artifacts", []) + data.get("local_source_baseline", [])
    wip = data.get("wip_entry")
    if isinstance(wip, dict):
        records.append(wip)
    elif data.get("state") != "complete":
        errors.append("Unfinished feature has no WIP entry in its checkpoint.")
    if not data.get("artifacts"):
        errors.append("Checkpoint has no artifact baseline.")
    for item in records:
        try:
            path = resolve_record(root, item, data)
            if not path.is_file():
                errors.append(f"Missing: {item['path']}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
                errors.append(f"Changed since checkpoint: {item['path']}")
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
    if data.get("state") != "complete" and isinstance(wip, dict):
        try:
            wp = resolve_record(root, wip, data)
            if wp.parent != root / "WIP" or not wp.name.endswith("_WIP.md"):
                errors.append("Active WIP entry must be WIP/<project-name>_WIP.md.")
        except ValueError:
            pass
    return errors


def refresh_records(root: Path, run: Path, data: dict) -> dict:
    """Refresh known files only; the agent still owns stages, decisions and WIP content."""
    for key in ("artifacts", "local_source_baseline"):
        for item in data.get(key, []):
            path = resolve_record(root, item, data)
            if key == "local_source_baseline" and record(root, path)["sha256"] != item["sha256"]:
                raise ValueError("Approved source copy changed; reconcile source version before saving.")
            item.update(record(root, path))
    if isinstance(data.get("wip_entry"), dict):
        path = resolve_record(root, data["wip_entry"], data)
        data["wip_entry"].update(record(root, path))
    data.update(schema_version=3, path_base="workspace", saved_date=date.today().isoformat())
    return data


def command_doctor(root: Path) -> int:
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    print(f"Workspace: {root}\nPython: {sys.version.split()[0]}")
    for name in missing:
        print(f"MISSING {name}")
    print('Codex CLI: ' + ('found; authentication not tested' if shutil.which('codex') else 'not found'))
    print('Claude Code: ' + ('found; authentication not tested' if shutil.which('claude') else 'not found'))
    print('OpenRouter: API connection setup available; key/network not tested')
    print('init requires one configured execution provider; local maintenance commands remain available.')
    print("AI provider/authentication: user configured; not tested by this command.")
    print("Figma/document tools and fonts: verify in each AI session; not bundled.")
    print("Local workspace structure: " + ("FAIL" if missing else "PASS"))
    return bool(missing)


def command_list(root: Path) -> int:
    statuses = sorted((root / "features").glob("*/status.md"))
    if not statuses:
        print("No projects. Use: new <feature-id> --name 'Project name'")
    for status in statuses:
        try:
            data = read_checkpoint(status.parent)
            print(f"{status.parent.name}\t{data.get('state', 'unknown')}\tstage {data.get('stage', '?')}")
        except (OSError, ValueError):
            print(f"{status.parent.name}\tcheckpoint missing/invalid; read status.md")
    return 0


def command_new(root: Path, slug: str, name: str | None, *, announce: bool = True) -> int:
    run = feature(root, slug)
    wip = root / "WIP" / f"{slug}_WIP.md"
    if (root / "WIP").is_symlink() or not contained(wip, root):
        raise ValueError("WIP directory must stay inside the workspace without a symlink.")
    if run.exists() or wip.exists():
        raise ValueError("Project or WIP entry already exists; use resume instead.")
    name = (name or slug.replace("-", " ").title()).strip()
    if not name or "\n" in name or "\r" in name:
        raise ValueError("Project name must be a nonempty single line.")
    # Read dependencies before creating directories; missing templates do not leave a partial run.
    templates = {n: (root / "templates" / f"{n}.md").read_text(encoding="utf-8")
                 for n in ("brief", "run-plan")}
    run.mkdir(parents=True)
    (run / "requirements").mkdir()
    wip.parent.mkdir(exist_ok=True)
    (run / "requirements/00-brief.md").write_text(templates["brief"], encoding="utf-8")
    (run / "01-run-plan.md").write_text(templates["run-plan"], encoding="utf-8")
    (run / "status.md").write_text(
        f"# {name}\n\nFeature ID: {slug}\nState: ready\nStage: 0 — intake\n"
        "Input revision: none supplied\nAccepted output revisions: none\n"
        "Approvals: none\nGate C2: not reached\nApproved variant scope: none\n"
        "Next action: ask for the brief or source path, target surface and intended deliverables.\n"
        f"WIP entry: WIP/{slug}_WIP.md (workspace-relative)\nUpdated: {date.today()}\n", encoding="utf-8")
    (run / "decisions.md").write_text("# Decisions\n\nNo product, design or output approvals recorded.\n", encoding="utf-8")
    (run / "change-log.md").write_text(f"# Change log\n\n{date.today()}: created project scaffold; no design work or approvals.\n", encoding="utf-8")
    (run / "RESUME.md").write_text(
        f"# Resume {name}\n\nRead workspace AGENTS.md and .agents/skills/design-workflow/SKILL.md, "
        "then this feature's status.md, decisions.md and checkpoint.json. "
        "Continue Stage 0 intake; no brief or approvals exist. Verify session capabilities before promising external work.\n", encoding="utf-8")
    wip.write_text(
        f"# {name} — WIP\n\nFeature ID: {slug}\nState: ready\nStage: 0 — intake\n"
        "Next action: obtain brief, target surface and deliverables. No approvals recorded.\n\n"
        f"[Status](../features/{slug}/status.md) · [Decisions](../features/{slug}/decisions.md) · "
        f"[Resume guide](../features/{slug}/RESUME.md)\n\n"
        f"Resume prompt: Resume feature {slug} from its saved checkpoint.\n", encoding="utf-8")
    data = {"schema_version": 3, "path_base": "workspace", "feature_id": slug,
            "name": name, "state": "ready", "stage": 0, "final_output_accepted": False,
            "approved_variant_build_scope": [], "gates": {"A_B": "pending", "C2": "not reached", "D": "pending"},
            "active_processes": [], "uncertain_write_outcomes": [], "local_source_baseline": [],
            "next_action": "Obtain brief, target surface and intended deliverables.",
            "wip_entry": record(root, wip), "artifacts": [record(root, p) for p in sorted(run.rglob("*.md"))]}
    data = refresh_records(root, run, data)
    (run / "checkpoint.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if announce:
        print(f"Created {slug}. No approvals or external designs created.\nNext: resume {slug}")
    return 0


def command_resume(root: Path, slug: str | None) -> int:
    if slug is None:
        print((root / "BOOTSTRAP.md").read_text(encoding="utf-8"))
        return 0
    run = feature(root, slug)
    if not (run / "status.md").is_file():
        raise ValueError("Project does not exist. Use list to find its feature ID.")
    print(f"Open your AI CLI with filesystem access to: {root}\n\nPaste this prompt:\n")
    print(f"Read AGENTS.md and .agents/skills/design-workflow/SKILL.md in this workspace. "
          f"Resume feature {slug}. Read features/{slug}/status.md, decisions.md, RESUME.md and checkpoint.json, "
          "and the checkpoint's WIP entry. Reconcile current files and external design nodes before writing. "
          "Preserve recorded approvals, deferrals and review limits. Continue only the saved next action. "
          "If this CLI has no skill loader, read the referenced Markdown files directly. "
          "Verify your own session tools; do not assume another teammate's connectors or credentials exist.")
    try:
        routing = model_router.configuration(root)
        print(f"\nSaved provider: {routing['provider']} / {routing['mode']}. Use task plan/run for routed execution.")
    except ValueError:
        print('\nNo execution provider configured. Run ./design-workspace providers setup before starting agent work.')
    return 0


def ask_required(prompt: str, default: str = "") -> str:
    while True:
        value = input(prompt).strip() or default
        if value:
            return value
        print("Please enter a value, or press Ctrl-C to cancel.")


def command_init(root: Path) -> int:
    """Collect local intake or select a saved run; never launch an AI session."""
    print(f"\nDesign Workspace\n{root}")
    if agent_runtime.ensure_provider(root) is None:
        return 0
    print('\n1. New project / feature\n2. Resume existing feature\n3. Change provider or models\n0. Exit\n')
    while True:
        choice = input('Choose New, Resume or Settings [1/2/3/0]: ').strip().lower()
        if choice in {'0', 'exit', 'q', 'quit'}:
            return 0
        if choice in {'3', 'models', 'providers', 'settings'}:
            try:
                agent_runtime.setup(root)
            except (ValueError, OSError) as exc:
                print(f'Setup did not finish: {exc}. Previous settings preserved; choose Settings to retry.')
            continue
        if choice in {'1', 'new', '2', 'resume'}:
            break
        print('Enter 1 (New), 2 (Resume), 3 (Provider/models), or 0 (Exit).')
    if choice in {"2", "resume"}:
        statuses = sorted((root / "features").glob("*/status.md"))
        if not statuses:
            print("No saved features yet. Run init again and choose New.")
            return 0
        print("\nSaved features:")
        for number, status in enumerate(statuses, 1):
            try:
                data = read_checkpoint(status.parent)
                detail = f"{data.get('state', 'unknown')} | stage {data.get('stage', '?')}"
            except (OSError, ValueError):
                detail = "checkpoint missing/invalid; reconcile status.md"
            print(f"{number}. {status.parent.name} | {detail}")
        while True:
            selected = input("\nSelect a feature number or ID [0 to exit]: ").strip()
            if selected.lower() in {"0", "exit", "q", "quit"}:
                return 0
            match = next((s for s in statuses if s.parent.name == selected), None)
            if match is None and selected.isdigit() and 1 <= int(selected) <= len(statuses):
                match = statuses[int(selected) - 1]
            if match is not None:
                return command_resume(root, match.parent.name)
            print("Choose one of the listed feature numbers or IDs.")

    # Gather everything before creating records, so cancellation leaves no partial intake.
    name = ask_required("\nProject / feature name: ")
    suggested = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    while True:
        slug = ask_required(f"Feature ID{f' [{suggested}]' if suggested else ''}: ", suggested)
        try:
            run = feature(root, slug)
            if run.exists() or (root / "WIP" / f"{slug}_WIP.md").exists():
                raise ValueError("That feature already exists. Choose another ID, or cancel and Resume.")
            break
        except ValueError as exc:
            print(exc)
    print("\nDescribe your requirements or paste a brief/source-file path.")
    print("Multiple lines are supported. Enter a single . on its own line to finish.")
    lines = []
    while True:
        line = input("> ")
        if line.strip() == ".":
            if any(s.strip() for s in lines):
                break
            print("Enter requirements or a source path before finishing.")
        else:
            lines.append(line)
    requirements = "\n".join(lines)
    surface = input("Target surface (web/mobile/etc.; Enter if undecided): ").strip()
    deliverables = input("Desired deliverables (Enter if undecided): ").strip()
    command_new(root, slug, name, announce=False)
    intake = {"requirements": requirements, "target_surface": surface,
              "desired_deliverables": deliverables, "approval": "not yet reviewed or approved"}
    (run / "requirements/intake.json").write_text(json.dumps(intake, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    brief = run / "requirements/00-brief.md"
    with brief.open("a", encoding="utf-8") as output:
        output.write("\n## User input collected by init\n\n"
                     "Raw input is saved in `intake.json`. Treat it as intake evidence; source files have not been read or copied, "
                     "requirements have not been reviewed, and no product/design approvals are recorded.\n")
    next_action = "Read requirements/intake.json and any referenced sources; reconcile the brief, then ask only necessary intake clarifications."
    status = run / "status.md"
    status.write_text(status.read_text(encoding="utf-8").replace("Input revision: none supplied", "Input revision: user intake captured in requirements/intake.json; sources not yet inspected").replace("Next action: ask for the brief or source path, target surface and intended deliverables.", f"Next action: {next_action}"), encoding="utf-8")
    resume = run / "RESUME.md"
    resume.write_text(f"# Resume {name}\n\nRead workspace AGENTS.md and .agents/skills/design-workflow/SKILL.md, then status.md, decisions.md and checkpoint.json.\n\nNext: {next_action}\nNo approvals recorded. Verify session tools before external work.\n", encoding="utf-8")
    cp = run / "checkpoint.json"
    data = read_checkpoint(run)
    data["next_action"] = next_action
    data["artifacts"].append(record(root, run / "requirements/intake.json"))
    wip = root / data["wip_entry"]["path"]
    wip.write_text(wip.read_text(encoding="utf-8").replace("Next action: obtain brief, target surface and deliverables.", f"Next action: {next_action}"), encoding="utf-8")
    data = refresh_records(root, run, data)
    cp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("\nRequirements saved. Continue in your AI tool using the prompt below.")
    return command_resume(root, slug)


def share_files(root: Path, slugs: list[str]) -> list[Path]:
    files = [root / name for name in RUNTIME_FILES]
    for name in RUNTIME_DIRS:
        files.extend(p for p in (root / name).rglob("*") if p.is_file())
    for slug in slugs:
        run = feature(root, slug)
        errors = check_feature(root, slug)
        if errors:
            raise ValueError("Cannot package invalid project: " + "; ".join(errors))
        data = read_checkpoint(run)
        if data.get("schema_version", 1) < 3:
            raise ValueError("Selected feature needs a portable schema 3 checkpoint first.")
        files.extend(p for p in run.rglob("*") if p.is_file())
        if isinstance(data.get("wip_entry"), dict):
            files.append(resolve_record(root, data["wip_entry"], data))
    output = []
    for path in sorted(set(files)):
        if not path.is_file():
            raise ValueError(f"Missing distribution file: {path}")
        if path.is_symlink() or not contained(path, root):
            raise ValueError(f"Symlink/outside-workspace file cannot be packaged: {path}")
        parts = path.relative_to(root).parts
        relative = path.relative_to(root).as_posix()
        if any(relative == local or relative.startswith(local + "/") for local in LOCAL_ONLY_PATHS):
            continue
        if any(p in {"__pycache__", ".git", ".aws", ".codex", ".claude", ".gemini", ".venv", "node_modules"} for p in parts):
            continue
        if path.name.startswith(".env") or path.suffix in {".pyc", ".pem", ".key"} or path.name.lower() in {"credentials", "credentials.json", "auth.json", "workspace.local.json", "workspace.local.json.tmp"}:
            continue
        output.append(path)
    return output


def command_pack(root: Path, output: Path, slugs: list[str]) -> int:
    output = output.resolve()
    if output.exists():
        raise ValueError("Archive already exists; choose a new --output path.")
    if output.suffix != ".zip":
        raise ValueError("Output must be a .zip file.")
    if any(contained(output, root / d) for d in (*RUNTIME_DIRS, "features", "WIP")):
        raise ValueError("Write the archive under dist/ or outside the workspace.")
    files = share_files(root, slugs)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
            for p in files:
                archive.write(p, "design-workspace/" + p.relative_to(root).as_posix())
    except Exception:
        output.unlink(missing_ok=True)
        raise
    print(f"Created {output}\nFiles: {len(files)}\nProjects: {', '.join(slugs) if slugs else 'none (clean starter)'}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Workspace location; defaults to this script's checkout")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Interactive New/Resume menu with requirements capture")
    sub.add_parser("doctor", help="Check local prerequisites; does not verify AI authentication")
    sub.add_parser("list", help="List saved project stages")
    models = sub.add_parser("models", help="Discover and configure account-specific task models")
    models.add_argument("action", choices=("list", "setup", "status"))
    models.add_argument("--provider", choices=("codex", "claude-code", "openrouter"))
    providers = sub.add_parser("providers", help="Detect and configure Codex CLI, Claude Code or OpenRouter")
    providers.add_argument("action", choices=("list", "setup", "status"))
    providers.add_argument("--provider", choices=("codex", "claude-code", "openrouter"))
    task = sub.add_parser("task", help="Plan or run a bounded read-only worker with model routing")
    task.add_argument("action", choices=("plan", "run"))
    task.add_argument("--provider", choices=("codex", "claude-code", "openrouter"))
    task.add_argument("feature_id")
    task.add_argument("kind", choices=model_router.KINDS)
    task.add_argument("--context", action="append", default=[], help="Workspace-relative feature text file; repeat for more")
    task.add_argument("--image", action="append", default=[], help="Workspace-relative feature image; repeat for more")
    new = sub.add_parser("new", help="Create a separate project and WIP entry without approvals")
    new.add_argument("feature_id")
    new.add_argument("--name")
    resume = sub.add_parser("resume", help="Print a provider-independent bootstrap or project resume prompt")
    resume.add_argument("feature_id", nargs="?")
    check = sub.add_parser("check", help="Validate portable paths, files and saved hashes")
    check.add_argument("feature_id", nargs="?")
    save = sub.add_parser("checkpoint", help="Refresh registered hashes after synchronizing project records and WIP")
    save.add_argument("feature_id")
    pack = sub.add_parser("pack", help="Create a clean starter ZIP; projects are excluded by default")
    pack.add_argument("--output", type=Path)
    pack.add_argument("--include-feature", action="append", default=[])
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "init": return command_init(root)
        if args.command == 'providers':
            if args.action == 'list':
                agent_runtime.list_providers(root)
                return 0
            if args.action == 'setup':
                agent_runtime.setup(root, args.provider)
                return 0
            print(json.dumps(model_router.read_local(root).get('agent_runtime', {'legacy_codex_settings': 'model_routing' in model_router.read_local(root)}), indent=2))
            return 0
        if args.command == 'models':
            if args.action == 'list' and args.provider in {None, 'codex'}:
                try:
                    selected = model_router.configuration(root, args.provider)['provider']
                except ValueError:
                    selected = args.provider or 'codex'
                if selected == 'codex':
                    model_router.display_catalog(model_router.discover(root))
                    return 0
            return agent_runtime.models(root, args.action, args.provider)
        if args.command == "task":
            run = feature(root, args.feature_id)
            errors = check_feature(root, args.feature_id)
            if errors:
                raise ValueError("Reconcile feature checkpoint before task execution: " + "; ".join(errors))
            return model_router.execute(root, run, args.kind, args.context, args.image, dry_run=args.action == "plan", provider=args.provider)
        if args.command == "doctor": return command_doctor(root)
        if args.command == "list": return command_list(root)
        if args.command == "new": return command_new(root, args.feature_id, args.name)
        if args.command == "resume": return command_resume(root, args.feature_id)
        if args.command == "pack": return command_pack(root, args.output or root / "dist/design-workspace-starter.zip", args.include_feature)
        if args.command == "checkpoint":
            run = feature(root, args.feature_id)
            data = refresh_records(root, run, read_checkpoint(run))
            (run / "checkpoint.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print("Refreshed registered hashes. Stages, approvals and WIP text were not inferred or changed. Register new artifacts explicitly in the manifest.")
            return 0
        slugs = [args.feature_id] if args.feature_id else [p.parent.name for p in sorted((root / "features").glob("*/status.md"))]
        failed = False
        for slug in slugs:
            errors = check_feature(root, slug)
            print(f"{slug}: {'FAIL' if errors else 'PASS'}")
            for error in errors: print(f"  {error}")
            failed |= bool(errors)
        if not slugs: print("No projects to check.")
        return int(failed)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
