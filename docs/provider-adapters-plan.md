# Codex, Claude Code and OpenRouter orchestration plan

Date: 2026-10-17. Status: roadmap; provider-first setup and report-worker adapters now implemented. See [implementation report](provider-implementation-report.md) for actual tests/support. Full stage-aware scheduling remains planned. Provider-first setup and bounded workers are implemented locally; live acceptance and the scheduler remain pending. Scope: the reusable CLI; existing feature/design work and approvals remain untouched.

## Intended outcome

A teammate clones the tool, runs `init`, selects their installed AI CLI, configures models once, and executes the same saved design workflow with that provider. Codex CLI, Claude Code and OpenRouter use shared source/artifact/checkpoint conventions and distinct execution adapters. The user confirmed provider-first init with these three options and no Manual workflow mode. Detailed branch/authentication/credential/error flows: [provider setup](provider-setup-flow.md). The tool must accurately distinguish portable workflow instructions, a bounded worker executor and a stage-aware orchestrator.

Recommended first release: all three providers support bounded text/report workers, model routing, usage evidence and resumable local state. A subsequent milestone adds automatic role scheduling within the existing workflow gates. Write-enabled Figma/design agents remain a separate capability requiring actual connector access and explicit scope.

## Baseline and verified evidence

Current code supports three execution providers through `scripts/providers/`, with shared setup in `scripts/agent_runtime.py` and routing/context/run records in `scripts/model_router.py`. Local profiles use `agent_runtime` version2 and retain legacy Codex settings. The latest suite passes46 tests, including security regression cases; see [audit and current progress](security-and-maintainability-review.md). These are synthetic/local tests, not live model acceptance. Earlier live Codex discovery was blocked by this session's state-directory permissions.

Read-only local checks during planning: `claude --version` reports2.1.287; `claude --help` exposes print, model, effort, structured-output and tool-control options. Installed does not mean authenticated or authorized. No Claude inference/authentication flow was launched.

Codex documents `model/list` with model/effort/input metadata; values depend on the client/account. Reuse it rather than hard-coding a catalog. [Official app-server reference](https://learn.chatgpt.com/docs/app-server).

Claude documents noninteractive print, JSON/schema output, model/effort selection, tool restrictions and session-persistence controls. Built-in tool restrictions alone do not cover MCP tools. Check the installed version and exact option combination. [Official CLI reference](https://code.claude.com/docs/en/cli-reference).

Claude model aliases/names and policy can affect the actual model; supplying `--model` is not itself a successful access check. Preserve requested selection and inspect reported actual model use. No equivalent account-wide machine-readable CLI catalog endpoint was established in this research; do not claim one is available or impossible. [Official model configuration](https://code.claude.com/docs/en/model-config).

## Startup and user experience

Provider setup is the first part of `init`, before New/Resume. This supersedes the earlier proposal to bury provider choice under option3 and to offer prompt-only/manual fallback.

```text
Choose your AI execution provider:
1. Codex CLI     [detected status]
2. Claude Code   [detected status]
3. OpenRouter    [connection status]
0. Exit
```

Detect CLI installation separately from authentication. OpenRouter uses a connection/credential reference, not an executable detector. After native login or secure API-key setup, configure model tiers, optionally perform a disclosed live test, and enter New/Resume. On later starts recheck the saved provider and reuse settings; invalid/unknown readiness prompts reconfiguration or explicit switching. With no configured provider, workflow execution does not start. Local maintenance remains available, but there is no Manual workflow execution mode.

Ask once for Economy/Balanced/Quality, tier models/native efforts and attempt policy. Codex uses its verified catalog; Claude uses supported discovery or explicitly labelled user configuration; OpenRouter uses authenticated connection checks and catalog capability filtering. Installed/catalogued/configured/authenticated/live-verified are separate states. API keys are hidden/session-only or explicitly referenced through environment/secure storage, never saved in workspace/project/Git files. Complete details and failure paths: [provider-setup-flow.md](provider-setup-flow.md).

## Adapter boundary and proposed files

Refactor before adding another provider's branches to the existing monolithic router:

```text
scripts/
  workspace.py                 CLI/menus and local file commands
  model_router.py              compatibility facade, policy and orchestration entry
  agent_runtime.py             provider-neutral task/run lifecycle
  providers/
    __init__.py
    base.py                    capability/selection/result contracts
    codex.py                   current Codex discovery and execution
    claude_code.py             Claude Code execution/configuration
    openrouter.py              API connection, model catalog and bounded API workers
    credentials.py             environment/session/secure-store references; no plaintext secrets
```

Each adapter supplies:

- `detect`: executable/version information, without installation or account modification.
- `capabilities`: structured output, native effort, model discovery, text/image input, tool isolation, usage, persistence and cancellation support. Use supported/unsupported/unknown rather than guessed booleans.
- `models`: catalog or explicitly labelled user configuration with provenance/time. Catalog visibility, syntax validation and successful inference are different states.
- `validate_selection`: provider-specific model, effort, account/policy errors and visual input readiness.
- `build_invocation`: argv/stdin/config confined to the task; no shell interpolation, global settings edits, copied credentials or approval bypass flags.
- `execute/normalize_result`: stream/final output, report validation, exit state, actual/requested model and native usage details.
- `cancel`: bounded timeout and child-process cleanup; preserve partial evidence without recording success.

Common routing, context selection/hashes, schema validation, ownership, run records and checkpoint rules belong outside the adapters. CLI authentication remains managed by the user's own CLI; OpenRouter uses the explicit credential flow in provider-setup-flow.md. Do not equate both providers' effort labels, permission modes, subscription usage or cost semantics.

## Task execution and model policy

Retain current kinds initially: extract, summarize, requirements, design, review, visual-review. Extract/summarize generally use the light tier, requirements the configured mode's tier, and independent review the strong tier. Complexity can justify explicit escalation; missing source policy or approval is a blocker, not something a larger model can solve. File/hash/scaffold operations remain Python-only.

Proposed commands (future syntax; not available yet):

```sh
./design-workspace providers list
./design-workspace providers setup
./design-workspace models setup --provider claude-code
./design-workspace task plan customer-portal requirements --provider claude-code --context features/customer-portal/requirements/00-brief.md
./design-workspace task run customer-portal requirements --provider claude-code --context features/customer-portal/requirements/00-brief.md
```

Resolve explicit `--provider`, then the saved local default. If neither exists, require setup for execution; never silently infer one from PATH ordering. No automatic cross-provider fallback, account switching or second-provider billing. An explicit provider change creates a fresh bounded task using approved source/artifact files, not the other provider's private chat/session/configuration. Keep the existing `models` commands compatible where possible.

Automatic retries stay within the selected provider and approved attempt limit. Transport/auth/invalid-schema failures do not trigger spend-producing retries. Record escalation reason and remaining attempts. Provider-native automatic model fallback must be disabled where possible or detected and surfaced; do not falsely claim the requested model executed.

## State, ownership and portability

Extend `workspace.local.json` with a versioned runtime settings section containing a default provider and separate per-provider routing configuration for codex, claude-code and openrouter. Store only credential references, never API keys. Preserve unrelated keys; migrate version1 Codex preferences atomically, retaining a local backup and existing model/effort choices. Never commit user settings or add them to starter/feature packages. No provider credentials belong in this file.

Feature `status.md`, `decisions.md`, WIP, sources, artifacts and schema3 checkpoints remain provider-neutral. Changing the execution provider does not approve scope or change stages. Continue the exact saved next action; never require new intake merely because a teammate changed AI clients.

Add a small committed `CLAUDE.md` entry document that points to AGENTS.md/BOOTSTRAP.md and local skill paths, if verified instruction discovery requires it. Keep the actual workflow rules in one source. Inspect how the entry point affects hooks/settings/tool loading before relying on it. No global client setup or native skill installation is required for reading Markdown.

Use one orchestrator/writer per feature/Figma area. Record explicit ownership before handoff; worker processes start independently and return reports. Before executing a stage-aware workflow, acquire a feature-run lock with owner/run identity and refuse a second writer. Stale locks require reconciliation, not silent takeover. A read-only reviewer never becomes a writer through model/provider fallback.

## Worker isolation and visual readiness

The first adapter-parity milestone is report-only. Compile required workflow/role instructions and explicitly selected source/design evidence into bounded context. Test tool exposure, hooks, subprocess behavior, MCP configuration and auth compatibility for each CLI. Claude plan mode or a built-in tool allowlist must not be treated as an equivalent filesystem/external-service sandbox. If the no-mutation contract cannot be enforced at the promised level, block the affected execution mode and explain the limitation rather than bypassing permissions.

Prefer tools-disabled analysis for supplied context when verified compatible with structured output and the user's CLI authentication. Disable external mutation channels explicitly; do not use a mode that unexpectedly requires a different credential type. For controlled file reading, permit only verified read facilities. Re-check the existing Codex adapter's external MCP/tool exposure as part of parity work; it currently has only filesystem sandbox plus worker instructions.

Visual-review requires actual image delivery to a vision-capable worker. A filename or caption is not image inspection. Implement/test provider-specific image transport separately; expose unsupported/unknown until verified. Continue text/source analysis without claiming complete visual review. Figma access is separate from CLI/model availability and must be checked in each user's session.

## Results and token/cost efficiency

Keep per-run evidence under ignored `features/<id>/history/agent-runs/<run-id>/`. Normalize provider, adapter/CLI version, task kind, mode/tier, requested model, resolved/actual model when reported, native effort, input/image hashes, timings, attempt/exit status, report, usage provenance and limits. Preserve raw native events privately for debugging.

Keep input/output/cache usage fields distinct, with missing values null. Provider-reported cost estimates are not necessarily invoices or subscription allowance consumption; preserve their meaning/currency/provenance and never invent a common dollar total. No per-account credentials or auth response blobs in run records. A complete report is not Stage4 completion or user acceptance.

Use selected context and independent role handoffs, not the full transcript for every worker. Bound retry count, context and runtime. Report measured usage when available; add hard token/spend controls only when actually enforceable by the specific adapter. Do not promise a percentage saving before benchmarking representative tasks and correction rates.

## Delivery milestones and acceptance

| Milestone | Work | Exit criteria |
| --- | --- | --- |
| 1. Shared contracts + Codex refactor | Extract lifecycle/policy from provider mechanics; preserve commands/settings and current behavior. | Original regression suite passes; migration/idempotency/cancellation tests added; no lost settings/feature changes. |
| 2. Provider-aware startup | Detection/readiness states, selection, local defaults, provider override and clear missing-client paths. | Neither/Codex-only/Claude-only/both/OpenRouter-only fixtures pass. Workflow waits for a configured provider. No Manual mode or automatic login/install/inference. |
| 3. Claude text-worker parity | Verified model/effort setup, invocation/output parsing, structured report and usage normalization; no-mutation controls. | Deterministic fake-CLI tests pass for success/error/auth/version/schema/timeout/model-remap cases. No unsupported capability silently enabled. |
| 4. OpenRouter setup + API workers | Secure key input/reference, non-inference connection/catalog checks, model routing and bounded report workers; controlled tool dispatcher for tool-dependent tasks. | OpenRouter-only user can configure and execute an explicit task without Codex/Claude; no key leaks or hidden generation/charge/fallback; tool capability tested before advertised. |
| 5. Live acceptance + visual capability | Explicit small real-account smoke task per provider, image transport test where supported, relocation/privacy review. | Capture version/config/usage evidence without credentials. Each claimed feature is verified or clearly marked unavailable; no untested end-to-end claim. |
| 6. Stage-aware orchestration | Planner schedules bounded analyst/strategist/planner/designer/reviewer/synthesizer tasks where useful; dependency checks, writer locks, pause/resume and gates. | Fixtures cannot bypass DRD, variant or final-acceptance decisions. Crash/restart resumes once without duplicate mutation. Reports are integrated by the orchestrator. External writes remain disabled unless separately implemented/authorized. |

Milestones1–4 have local implementations and automated coverage. Milestone5 remains incomplete: real account inference and image acceptance have not been verified. Milestone6 completes the next major orchestration layer; native subagent features are an adapter capability, not mandatory or a reason to start seven processes. Parallelism initially limited to independent read-only tasks; one writer per feature.

## Verification and release checklist

- Unit/contract tests for all adapters using synthetic models and scrubbed native payload fixtures; no paid inference in routine tests.
- Configuration migration, route selection, unavailable model/effort, unknown capabilities, one-attempt default, two-attempt ceiling and no automatic cross-provider retry.
- CLI integration tests for setup menus, missing/old binaries, unverified auth, parsing failures, process hangs and cancellation/cleanup.
- No-change tests for source bytes, feature gates/decisions, stale checkpoint refusal, source/context containment and ownership collisions.
- Privacy tests: settings, credentials, worker prompts/logs, real projects and WIP excluded from Git/default packages. Explicit feature transfer remains deliberate.
- Cross-provider handoff test: providerA's approved artifact/checkpoint can be resumed by providerB without copying chat/auth or losing deferrals. Conflicting state blocks execution until reconciled.
- Cross-platform checks for supported OS/executable forms; do not infer Windows support from POSIX fixtures.
- Update README, BOOTSTRAP, CLAUDE entry point if needed, team setup, command help and implementation report. Rebuild ZIP only for an intentional offline release; GitHub remains normal distribution.

## Pending decisions and exact continuation

Recommended defaults: provider-neutral shared state; one local default provider; explicit per-task override; Balanced routing; strong independent review; no automatic provider fallback; no Manual mode; provider-first native login or secure API setup; report-only workers first; no published model IDs/prices as account guarantees. The user confirmed the three-provider startup and removal of Manual workflow. This does not grant approval of paid acceptance tests, external writes or future product stages.

Current continuation: complete live account acceptance for the implemented provider setup/report workers, then address verified image capability and later stage-aware scheduling. Claude text-worker code is implemented and fixture-tested; live readiness remains unverified. Preserve existing feature approvals and deferrals. See the audit report for the current exact continuation.
