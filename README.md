# Design Workspace

A shared folder and local CLI for resumable design work with your team's own AI tools. It stores workflow instructions, project artifacts, approvals and WIP checkpoints. It does not supply a model, credentials or Figma access.

## Team quick start

1. Unzip the starter or copy the workspace to a local folder.
2. Use Python 3.10 or newer. No third-party Python packages are needed.
3. Open a terminal in the workspace and run:

```sh
python3 scripts/workspace.py doctor
python3 scripts/workspace.py init
```

4. Choose **New** to enter requirements, or **Resume** to select a saved feature.
5. Open that same folder in your preferred AI CLI and paste the printed continuation prompt. The menu saves intake locally; it does not launch an AI session.

On macOS/Linux use `./design-workspace` as a shortcut. On Windows use `py -3 scripts/workspace.py` or `python scripts/workspace.py` with Python 3.10+. If using Codex, launch `codex` from this folder. Other clients can read the instructions explicitly; no automatic loading or authentication is assumed.

From this checkout, the short command is `./design-workspace init`. See [interactive startup](docs/init-cli.md) for the exact terminal flow.

## Local CLI

```sh
python3 scripts/workspace.py init
python3 scripts/workspace.py doctor
python3 scripts/workspace.py list
python3 scripts/workspace.py new customer-portal --name "Customer Portal"
python3 scripts/workspace.py resume customer-portal
python3 scripts/workspace.py check customer-portal
python3 scripts/workspace.py checkpoint customer-portal
python3 scripts/workspace.py pack --output dist/team-starter.zip
```

- `init`: interactive New/Resume menu. New collects a name, ID, multiline requirements or source path (finish with a single `.` line), optional target surface and deliverables. Resume lists saved features and accepts a number or ID. Ctrl-C cancels. New records stay at Stage 0 with no approvals; referenced files are read later by your AI.
- `doctor`: check local files/Python; does not authenticate providers or connectors.
- `list`: show saved project states and stages.
- `new`: scaffold separate intake records and WIP; creates no designs/approvals and refuses existing IDs.
- `resume`: print a bootstrap or feature-specific prompt; does not launch a model.
- `check`: validate registered files, paths and hashes. Omit the ID to check all projects. This is local integrity checking, not design review or approval verification.
- `checkpoint`: refresh registered artifact/WIP hashes after synchronizing records. Update stage/scope fields and register new files explicitly; the command never infers approvals or WIP text. It refuses changed source snapshots.
- `pack`: make a clean starter ZIP without feature/WIP content. Add `--include-feature <id>` only for a project you intend to transfer. Existing archives are not overwritten.

Schema 3 checkpoint file records are workspace-relative, with `path_base: workspace`, so copies work on another machine. External source origins remain provenance; verified local source snapshots are the portable baseline.

## Workflow and files

Brief → Requirements → DRD → Main screens → Variant decision → Approved variants (if any) → Review → Handoff.

Keep requirement/DRD, new visual-direction, variant and final-acceptance gates. Deferring states permits a main-screen-only review, not a claim of full coverage. CTZPay Word finalization retains its separate approval requirement. Use the CTZPay skill only for relevant projects; do not apply its branding or product rules to generic projects.

```text
WIP/<project-name>_WIP.md
features/<feature-id>/
  sources/        # Unchanged inputs and provenance
  requirements/   # Brief, requirements and DRD
  design/         # Screen index, Figma links, style/state plans
  reviews/        # Review reports and evidence
  handoff/        # Delivery notes
  exports/        # Requested exports only
  history/        # Earlier versions
  status.md
  decisions.md
  01-run-plan.md
  RESUME.md
  checkpoint.json
  change-log.md
```

Create folders only as needed. Status and decisions are authoritative; WIP is the synchronized resume entry and history preserves prior versions. Backtick artifact paths in project documents are feature-relative unless specified otherwise; Markdown links are document-relative. Checkpoint file records are workspace-relative.

Start another project in a new AI chat: `Start a new design project called <name>. Keep the existing project saved.` Return with `Resume feature <feature-id> from its saved checkpoint.` Saved files restore context without requiring cross-chat memory.

## Share and maintain

Two reusable skills are bundled: workflow orchestration under `.agents/skills/design-workflow/` and [UI/UX Design Review](skills/ui-ux-design-review/SKILL.md) under `skills/`. The reviewer is routed explicitly from AGENTS.md at Stage 4; it checks approved DRD coverage and screen usability separately and does not edit designs. Clients can read both skills directly without global installation. Project-specific DRD converters and branded assets are optional local additions, excluded from Git and clean starter packages.

See [team setup](docs/team-setup.md), [workspace instructions](AGENTS.md) and the [workflow skill](.agents/skills/design-workflow/SKILL.md). The default starter excludes projects, WIP entries, provider configuration and common credential/cache files. Packaging is not a comprehensive secret/content audit. Selected transfers include source snapshots and history; review content before distributing.

Figma/document connectors, fonts, renderers and external skills are not bundled. Each teammate verifies their own tools, access and authentication. Continue independent planning when a connector is absent; do not claim unverified operations. Optional agents/openai.yaml metadata can be ignored by other clients. Do not store credentials here or change global client configuration.

## Git repository scope

This repository contains the reusable CLI, instructions, generic skills, templates, standards, documentation and synthetic test fixtures. Local `features/`, `WIP/`, `dist/`, provider settings, credentials, copied project-specific skills/assets and pilot planning records are ignored. Starting or resuming a feature does not make it part of the tool repository. Never force-add local project work when publishing the tool.

After cloning, run `./design-workspace doctor`, then `./design-workspace init`. No existing feature is required. See [repository scope](docs/repository-scope.md).
