# Interactive startup

On macOS/Linux, open a terminal and run:

```sh
cd /path/to/design-workspace
./design-workspace init
```

Teammates use the path to their own checkout. The portable equivalent is `python3 scripts/workspace.py init`; on Windows use `py -3 scripts/workspace.py init` with Python 3.10+.

```text
Design Workspace

1. New project / feature
2. Resume existing feature
0. Exit

Choose New or Resume [1/2/0]:
```

## New

Enter `1` or `new`. The CLI asks for:

1. Project/feature name.
2. Feature ID, with a suggested lowercase ID. Existing IDs are refused.
3. Requirements or a source-file path, across multiple lines. Finish by entering a single `.` on its own line. At least one nonempty line is required.
4. Target surface, optional if undecided.
5. Desired deliverables, optional if undecided.

Input is collected before creating the feature; Ctrl-C or an input EOF before submission cancels without creating it. New records are separate under `features/<id>/` with one `WIP/<id>_WIP.md`. Exact requirements, surface and deliverables are saved in `requirements/intake.json`; the brief points to that input. Source paths are captured as text; originals are not read/copied by this helper. The AI must read inputs, preserve source snapshots and complete intake. No requirements/design/variant approvals are granted.

## Resume

Enter `2` or `resume`. The CLI lists saved feature IDs with their recorded state and stage. Select by number or exact ID; enter `0` to exit. A missing/invalid checkpoint is labelled so the AI can reconcile it with status.md. If no features exist, the command explains how to start New. Merely selecting a feature does not change its files, stage, approvals or ownership.

## Continue with your AI

The command prints a feature-specific continuation prompt. Open your AI CLI in this same workspace and paste it. Read local AGENTS.md and skills explicitly if the client does not discover them. The helper does not connect a model, launch an AI session, configure credentials or authenticate Figma. Every session uses its own tools/access.

After closing the terminal, run the same `init` command and choose Resume. State is restored from saved files, not chat memory. Before switching features ask the AI to save its records/WIP and refresh/check the checkpoint. The menu does not save unsaved work from another active AI session.

Each feature retains its own saved stage and next action. New projects remain separate. Use one writer per feature/Figma area and record ownership before handoff.

Use the full command `./design-workspace init`; a bare system command named `init` is not this workspace helper.
