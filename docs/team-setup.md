# Team setup and project transfer

## Each person supplies

- A local workspace copy and Python 3.10+ for the helper. No pip packages are needed.
- Their own AI CLI with filesystem access. Use BOOTSTRAP.md if it does not discover AGENTS.md or skills automatically.
- Their own provider login/settings outside this folder. Do not copy another person's tokens.
- Their own permitted Figma account and callable connector when needed. File links are records, not access grants. Verify tools in each session.
- Document/image tools, fonts and skills only when required. Local planning works without Figma. The helper does not render documents or authenticate external tools.

Tool names and approval UIs vary. Read skill Markdown directly and use available equivalent tools. Record missing capabilities rather than inventing completed operations. Optional agents/openai.yaml metadata can be ignored by other clients.

At Stage 4, explicitly read `skills/ui-ux-design-review/SKILL.md` as routed by AGENTS.md. It reviews the approved DRD against actual evidence and independently assesses usability. The reviewer writes its report only; the orchestrator performs authorized design fixes. The folder is included in new starter packages and needs no native skill loader or global installation. Older starter ZIPs do not contain this addition; use the updated review-skill starter.

## Launch, start and switch

```sh
python3 scripts/workspace.py doctor
python3 scripts/workspace.py init
python3 scripts/workspace.py resume
python3 scripts/workspace.py new project-one --name "Project One"
python3 scripts/workspace.py list
python3 scripts/workspace.py resume project-one
```

Use `init` to configure/recheck Codex CLI, Claude Code or OpenRouter first, then enter New/Resume. There is no Manual workflow mode. New collects requirements; Resume lists saved features for selection. Finish multiline requirements with a single `.` line. Optional surface/deliverables can be left undecided. New/Resume launches no AI process and infers no approval. Init option 3 configures per-user model routing; explicit `task run` invokes a bounded report worker through the selected provider. See [interactive startup](init-cli.md).

Open the same folder in your AI CLI and paste the printed prompt. On Windows use `py -3 scripts/workspace.py` or `python scripts/workspace.py` with Python 3.10+. On macOS/Linux the shortcut is `./design-workspace`.

`new` scaffolds intake records without sources, designs or approvals. `resume` prints a prompt, not a model invocation. The AI still performs intake or follows the exact saved next action. Before switching people/projects, save stage, decisions, approvals/deferrals, verification limits and pending operations; synchronize WIP. Use one active writer per feature/Figma area and record ownership in the run plan.

For shorter commands, configure the optional `dw` shell alias/function described in [README](../README.md#short-command-dw). It points to your own checkout and does not copy settings or credentials.

## Per-teammate model routing

Run `./design-workspace providers setup` with your own chosen provider. Codex and Claude Code use native sign-in; OpenRouter uses hidden session input or OPENROUTER_API_KEY. Local profiles and light/standard/strong mappings stay in ignored workspace.local.json and are excluded from packages. Keys are not persisted in files. Optional live tests explicitly consume your own allowance/credits and default to no. Read [routing](model-routing.md) and [implementation report](provider-implementation-report.md) for supported capabilities and limitations.

## Save a checkpoint

1. Update status, decisions, resume instructions, WIP and affected deliverables.
2. Synchronize checkpoint stage/scope fields with actual recorded decisions. Register new artifacts explicitly.
3. Required file records use workspace-relative paths with `path_base: workspace` in schema 3. Preserve source snapshots unchanged.
4. Run `python3 scripts/workspace.py checkpoint <id>`, then `python3 scripts/workspace.py check <id>`.

The helper refreshes registered hashes but never infers stages, approvals or WIP text. It refuses changes to registered source snapshots. Hashes verify integrity, not semantic agreement, design quality or external service state.

## Share the reusable tool

GitHub is the default distribution/update path:

```sh
git clone https://github.com/minnkoaung/design-workspace.git
cd design-workspace
./design-workspace doctor
./design-workspace init
```

For an existing clone, save work then use `git pull --ff-only`; reconcile local tool changes or divergent history explicitly. On Windows use the Python entry point described above. Each teammate supplies their own AI tool/authentication. Without Codex, select Claude Code or OpenRouter during setup. One provider must be configured before init enters New/Resume; local maintenance remains available without one. No CLI/account is installed automatically.

A clean starter ZIP is optional for offline distribution:

```sh
python3 scripts/workspace.py pack --output dist/team-starter.zip
```

It contains no feature folders or active WIP entries and excludes personal settings/credential/cache paths. Existing archives are not overwritten; choose a new output filename when needed. A ZIP is a static snapshot, not required alongside a GitHub clone and not automatically updated. Packaging is not a comprehensive secret/content audit.

## Transfer a selected project

```sh
python3 scripts/workspace.py check project-one
python3 scripts/workspace.py pack --include-feature project-one --output dist/project-one-transfer.zip
```

Selected transfers include sources, outputs, history and matching WIP. History/provenance may contain old machine paths and project information; these are evidence, not required runtime paths. Review selected content before sharing; no secret scan or licensing approval is implied.

The recipient should extract into a separate folder, run `doctor`, `check project-one`, then `resume project-one`. Reconnect tools under their own account and compare actual Figma nodes before writing. External original-source paths are informational; use verified local snapshots. Resolve missing required sources explicitly.

ZIP transfer provides no live synchronization. With Git/shared storage, coordinate editing and resolve conflicts in source authority, approvals, status and Figma changes before refreshing hashes. Never resolve approval conflicts by timestamp alone. The helper does not commit, push, publish or send files.

## Limits

`doctor` checks local prerequisites; `check` verifies registered local paths/hashes. Tests exercise local CLI behavior and relocation. AI instruction following, connectors, fonts, renderers, Windows execution and Figma writes require verification in each recipient's environment.
