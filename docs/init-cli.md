# Interactive startup

```sh
cd /path/to/design-workspace
./design-workspace init
```

Use your own checkout path. On Windows use `py -3 scripts/workspace.py init`; Python3.10+ is required.

Init first rechecks the saved provider, or offers Codex CLI, Claude Code and OpenRouter setup. There is no Manual workflow mode. With no configured provider you can set one up or exit; New/Resume is not shown early. Local list/check/doctor commands remain available independently.

Setup uses native CLI login/status for Codex/Claude, or environment/hidden-session OpenRouter credentials. It asks once for routing mode/models and optionally a clearly disclosed live test. No automatic installation, copied credentials or silent provider fallback. Details: [provider flows](provider-setup-flow.md), [current implementation](provider-implementation-report.md).

Once configured:

```text
1. New project / feature
2. Resume existing feature
3. Change provider or models
0. Exit
```

New collects name, unique lowercase feature ID, multiline requirements/source path (finish with a single `.` line), optional surface and deliverables. Input is gathered before feature creation; cancellation leaves no partial intake. It saves raw intake under requirements/intake.json, Stage0 records and one WIP entry. Sources are not automatically approved/read/copied by scaffold creation.

Resume lists saved features by number/ID and their state/stage. Selection does not change approvals or design state. Read status, decisions, RESUME and checkpoint; reconcile actual external nodes before writing. A missing/invalid checkpoint is labelled for reconciliation.

New/Resume records and prints the next-action context; actual bounded agent execution uses task plan/run with your configured provider. Resume printing does not by itself invoke a model. This release is not a complete automatic stage scheduler. Workflow gates, product decisions and final acceptance remain human/orchestrator responsibilities.

Option3 can change provider/model settings without overwriting projects. A canceled/failed setup preserves previous valid settings. Session-only OpenRouter keys may require hidden re-entry in a new process; environment references can be reused. Existing interactive chats are not silently switched to another model.

Close/reopen the terminal and use init again to resume from files, not old chat memory. Save ongoing work/records and refresh/check its checkpoint before switching projects or writers. The menu cannot save unsaved work from a different active AI session. Use the full `./design-workspace init`, not the operating system's unrelated `init` command.
