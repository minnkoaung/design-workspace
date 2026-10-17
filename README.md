# Design Workspace

A CLI foundation for resumable design-agent orchestration with **Codex CLI, Claude Code or OpenRouter**. It stores approved sources, project artifacts, decisions and WIP checkpoints; selects models by task; and executes bounded report workers through the selected provider.

Current scope: provider setup, model routing and explicit analysis/report tasks. Automatic end-to-end role scheduling and write-enabled Figma agents remain future work. Each teammate supplies their own account and permitted connectors. Current progress, security fixes and remaining work: [audit and continuation](docs/security-and-maintainability-review.md).

## Start from GitHub

```sh
git clone https://github.com/minnkoaung/design-workspace.git
cd design-workspace
./design-workspace doctor
./design-workspace init
```

Python 3.10+ is required; no third-party Python packages are needed. On Windows use `py -3 scripts/workspace.py <command>` instead of the shell launcher. Windows process behavior is not yet live-verified.

Init checks the saved provider, or starts with:

```text
Choose your AI execution provider:
1. Codex CLI
2. Claude Code
3. OpenRouter
0. Exit
```

After provider/model setup:

```text
1. New project / feature
2. Resume existing feature
3. Change provider or models
0. Exit
```

There is **no Manual workflow mode**. Without a configured provider, init does not enter New/Resume. Local maintenance commands such as list/check/doctor remain available. Missing Codex does not block Claude Code or OpenRouter; OpenRouter needs neither CLI.

## Short command: `dw`

The launcher already replaces `python3 scripts/workspace.py`: use `./design-workspace init` from the checkout.

For an even shorter command in zsh/bash, run these once from your checkout:

```sh
alias dw="\"$PWD/design-workspace\""
dw --help
dw init
```

This captures this checkout's absolute path, including spaces, so `dw` also works from other directories. Commands use this checkout's projects and settings. Examples:

```sh
dw list
dw resume customer-portal
dw providers setup
dw task plan customer-portal requirements
```

The alias lasts for the current terminal session. Run `alias dw` to print its resolved definition; copy that line into your own `~/.zshrc` (zsh) or `~/.bashrc` (bash) to keep it. Open a new terminal or reload that file. Each teammate uses their own checkout path; recreate the alias after moving it. The tool does not edit shell configuration. To remove the current alias, use `unalias dw`.

For PowerShell, add a function to your own session/profile instead, replacing the example path:

```powershell
function dw { py -3 'C:\path\to\design-workspace\scripts\workspace.py' @args }
dw init
```

Windows execution remains unverified. Neither shortcut installs Python or authenticates a provider.

## Provider setup

| Provider | Setup | Current worker scope |
| --- | --- | --- |
| Codex CLI | Detect executable → native login status/sign-in → discover catalog → choose tier models/efforts. | Text and CLI image input; read-only filesystem sandbox. External tool access remains native-policy dependent. |
| Claude Code | Detect required controls → native subscription or Console sign-in → enter model aliases/IDs. | Tools-disabled text reports; empty strict MCP config and non-managed hooks disabled. Managed policy can still apply. Image input is blocked until verified. |
| OpenRouter | Existing `OPENROUTER_API_KEY` or hidden session-only input → validate key/catalog → choose models. | API text/image reports and bounded feature-contained read tool where model supports tools. No shell, writes or MCP tools. |

No automatic installation or copying of provider credentials. Native CLI authentication remains managed by that CLI. OpenRouter keys are never written to workspace settings, logs or Git. Hidden input requires a terminal. Session-only keys are requested again in a later process; secure persistent key storage is not implemented. Use an environment reference for reusable access.

Setup offers an **optional disclosed live test**; default is no inference. Authentication/catalog checks do not prove model access or credit balance. Claude IDs are user-configured rather than a fabricated account catalog. Pricing rankings and token savings are not guessed.

```sh
./design-workspace providers list
./design-workspace providers setup --provider claude-code
./design-workspace providers setup --provider openrouter
./design-workspace models status
```

Preferences are per checkout/user in ignored `workspace.local.json`. Separate provider profiles and explicit per-task overrides are supported. Legacy Codex settings are preserved when adding a new provider. No automatic provider fallback or transfer of project content to another service.

See [setup flows](docs/provider-setup-flow.md) and [implementation/test report](docs/provider-implementation-report.md).

## Run a bounded task

Create a feature using init, then select relevant feature-local source files:

```sh
./design-workspace task plan customer-portal requirements --context features/customer-portal/requirements/00-brief.md
./design-workspace task run customer-portal requirements --context features/customer-portal/requirements/00-brief.md
```

Override the saved default only with an already-configured provider:

```sh
./design-workspace task run customer-portal review --provider claude-code --context features/customer-portal/sources/approved-drd.md
```

Kinds: `extract`, `summarize`, `requirements`, `design`, `review`, `visual-review`. Economy/Balanced/Quality select light/standard/strong tiers; review uses strong. Python handles deterministic file/hash operations without inference. Plan does not authenticate or call a model; run uses your provider allowance/billing.

Reports, requested/actual model evidence, native usage and attempts are saved under `features/<id>/history/agent-runs/`. Workers do not approve output, edit designs or advance stages. The orchestrator reviews/integrates reports and synchronizes checkpoints. Model status `complete` means report produced, not human acceptance.

Default one attempt; optionally at most one next-tier escalation. No automatic auth/network/invalid-output retry. Selected source text, images, tool reads and runtime are bounded; these are not a universal hard token/spend ceiling. Unknown usage/cost remains unknown. See [routing and execution](docs/model-routing.md).

## Available commands

Examples use the optional `dw` shortcut above. Without it, replace `dw` with `./design-workspace` from the checkout. `<id>` means your saved feature ID; `<kind>` is one of the task kinds listed below.

| Command | Description |
| --- | --- |
| `dw --help` | Show all top-level commands and global options. |
| `dw <command> --help` | Show syntax and options for a command, for example `dw task --help`. |
| `dw init` | Check/configure a provider, then open the New/Resume menu and collect requirements for new work. |
| `dw doctor` | Check Python, installed CLI executables and required workspace files; does not verify login or model access. |
| `dw list` | List saved features and their recorded stages/status. |
| `dw new <id> --name "Project Name"` | Create a separate feature scaffold and WIP entry without approvals. Use `init` for guided requirements capture. |
| `dw resume` | Print the generic AI bootstrap prompt. |
| `dw resume <id>` | Print the feature's saved continuation prompt; does not launch an agent. |
| `dw providers list` | Show available provider choices and CLI installation status without authenticating. |
| `dw providers setup` | Choose a provider, complete native/key setup and configure model tiers. Live inference testing is optional. |
| `dw providers status` | Show saved local runtime profiles; does not recheck live readiness. |
| `dw models list` | Show the selected provider's catalog, or configured Claude IDs. May make authentication/catalog requests; does not run generation. Without a profile, defaults to Codex discovery. |
| `dw models setup` | Open provider/model setup; equivalent setup flow to `providers setup`. |
| `dw models status` | Show the selected provider's saved routing, tiers and limits without inference. |
| `dw task plan <id> <kind>` | Validate the checkpoint and show the selected model/input plan without authentication or inference. |
| `dw task run <id> <kind>` | Validate the checkpoint and execute a bounded report worker using the provider's allowance/credits. |
| `dw check` | Validate all saved features' registered paths, files and hashes. |
| `dw check <id>` | Validate one feature's registered paths, files and hashes. |
| `dw checkpoint <id>` | Refresh registered hashes after you synchronize records and WIP; does not infer approvals, stages or register new artifacts. |
| `dw pack` | Create a project-free starter ZIP at `dist/design-workspace-starter.zip`; refuses to overwrite an existing archive. |
| `dw pack --output dist/team-starter.zip` | Create a project-free starter ZIP at the chosen path. |
| `dw pack --include-feature <id> --output dist/feature-transfer.zip` | Include an explicitly selected feature and its matching WIP in a transfer ZIP; review private contents before sharing. |

| Option | Applies to | Description |
| --- | --- | --- |
| `--root /path/to/checkout` | Global; place before the command | Use a different workspace, for example `dw --root /path/to/checkout list`. |
| `--provider <provider>` | `providers setup`, `models`, `task` | Select `codex`, `claude-code` or `openrouter`. Task execution requires that provider's existing profile; it does not silently fall back. |
| `--context features/<id>/sources/brief.md` | `task plan`, `task run` | Add a feature-local UTF-8 evidence file; repeat for more files, up to 10. |
| `--image features/<id>/design/screen.png` | `task plan`, `task run` | Add a feature-local image; repeat up to 5. Required for `visual-review`; Claude image transport is blocked. |
| `--name "Project Name"` | `new` | Set a display name; the feature ID remains the folder identifier. |
| `--include-feature <id>` | `pack` | Explicitly include a feature; repeat to transfer several. Projects are excluded by default. |
| `--output path.zip` | `pack` | Choose a new ZIP destination. |

Task kinds: `extract`, `summarize`, `requirements`, `design`, `review`, `visual-review`. All currently produce analysis/reports; the `design` kind does not write Figma designs. `review` and `visual-review` route to the strong tier. Worker completion never grants user acceptance.

## Local commands and project records

```sh
./design-workspace list
./design-workspace new customer-portal --name "Customer Portal"
./design-workspace resume customer-portal
./design-workspace check customer-portal
./design-workspace checkpoint customer-portal
```

New scaffolds Stage0 without approvals. Init collects multiline requirements (finish with a single `.` line), optional surface and deliverables. Source paths are evidence to read/preserve later. Resume prints saved context/next-action instructions; it does not itself invoke a worker. Use task plan/run for actual routed execution. Check validates registered local paths/hashes, not design quality or approval correctness. Checkpoint refreshes registered hashes after records are synchronized; it never infers stages or approvals.

```text
WIP/<project-name>_WIP.md
features/<feature-id>/
  sources/        # Unchanged source snapshots and provenance
  requirements/   # Intake, requirements and DRDs
  design/         # Screen index, Figma links and state plans
  reviews/        # Reviews and evidence
  handoff/        # Delivery notes
  exports/        # Requested exports
  history/        # Prior versions and private worker run records
  status.md
  decisions.md
  01-run-plan.md
  RESUME.md
  checkpoint.json
  change-log.md
```

Status/decisions are authoritative; WIP is the synchronized discovery/resume entry. Schema3 checkpoints use workspace-relative required paths. Preserve approvals, original source bytes and deferred variants. Workflow: Brief → Requirements → DRD → Main screens → Variant decision → Review → Final acceptance/handoff. A main-screen-only acceptance does not imply complete state/runtime coverage.

## Share, update and portability

GitHub clone/pull is the normal distribution/update path. Save active work and use `git pull --ff-only`; reconcile local tool edits/divergent history instead of overwriting them. Git ignores projects, WIP, credentials, provider settings, copied branded assets and generated dist files. Never force-add private work.

A ZIP is optional for offline distribution, not required alongside GitHub:

```sh
./design-workspace pack --output dist/team-starter.zip
```

Existing archives are not overwritten; choose a new filename if needed. Deliberate project transfer uses `pack --include-feature <id>` after checking/reviewing its contents. A ZIP is a static snapshot, not live synchronization.

Portable Markdown skills include workflow orchestration and approved-DRD/UI/UX review. [AGENTS.md](AGENTS.md) is authoritative; [CLAUDE.md](CLAUDE.md) points Claude Code to the same rules. No global skill install, personal settings, model account, Figma connector or credentials are bundled. Other clients may read the files, but only the three implemented adapters are execution choices; no prompt-only Manual mode is offered by init.

Read [team setup](docs/team-setup.md), [bootstrap](BOOTSTRAP.md), [repository scope](docs/repository-scope.md) and [provider implementation report](docs/provider-implementation-report.md) for current verification limits. Full stage-aware multi-role scheduling is described in the [roadmap](docs/provider-adapters-plan.md), not claimed complete.
