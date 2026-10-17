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

Use `init` for a guided New/Resume menu: New collects requirements; Resume lists saved features for selection. Finish multiline requirements with a single `.` line. Optional surface/deliverables can be left undecided. No AI process is launched and no approval is inferred. See [interactive startup](init-cli.md).

Open the same folder in your AI CLI and paste the printed prompt. On Windows use `py -3 scripts/workspace.py` or `python scripts/workspace.py` with Python 3.10+. On macOS/Linux the shortcut is `./design-workspace`.

`new` scaffolds intake records without sources, designs or approvals. `resume` prints a prompt, not a model invocation. The AI still performs intake or follows the exact saved next action. Before switching people/projects, save stage, decisions, approvals/deferrals, verification limits and pending operations; synchronize WIP. Use one active writer per feature/Figma area and record ownership in the run plan.

## Save a checkpoint

1. Update status, decisions, resume instructions, WIP and affected deliverables.
2. Synchronize checkpoint stage/scope fields with actual recorded decisions. Register new artifacts explicitly.
3. Required file records use workspace-relative paths with `path_base: workspace` in schema 3. Preserve source snapshots unchanged.
4. Run `python3 scripts/workspace.py checkpoint <id>`, then `python3 scripts/workspace.py check <id>`.

The helper refreshes registered hashes but never infers stages, approvals or WIP text. It refuses changes to registered source snapshots. Hashes verify integrity, not semantic agreement, design quality or external service state.

## Share the reusable tool

```sh
python3 scripts/workspace.py pack --output dist/team-starter.zip
```

Give teammates the ZIP; open its inner `design-workspace` directory. The clean starter contains CLI, instructions, bundled local skills, templates, standards and docs, with no feature folders or active WIP entries. It excludes personal provider configuration and common credential/cache paths. No account is connected by extraction. Packaging is not a comprehensive secret/content audit.

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
