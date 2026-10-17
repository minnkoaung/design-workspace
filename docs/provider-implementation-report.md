# Three-provider setup and execution — implementation report

Date: 2026-10-17. Implemented: provider-first setup, local profiles/model routing and explicit bounded report-worker execution for Codex CLI, Claude Code and OpenRouter. No Manual workflow mode. Full automatic stage-aware role scheduling is not implemented.

## What changed and where

| Location | Delivered behavior |
| --- | --- |
| `scripts/workspace.py` | Init requires a configured/rechecked provider before New/Resume. Added providers list/setup/status, provider-aware models commands and task provider override. Local maintenance commands remain independent. |
| `scripts/agent_runtime.py` | Provider selection, native auth/key setup handoff, tier configuration, optional disclosed live test, local profile persistence and legacy migration. No automatic login/installation/inference test. |
| `scripts/model_router.py` | Shared context/instruction compiler, policy, checkpoint-compatible plan/run lifecycle, attempt limits and private provider/usage evidence. Native adapter execution replaces Codex-only worker mechanics. Legacy Codex settings remain readable. |
| `scripts/providers/codex.py` | Native Codex status/sign-in, catalog, model/effort selection and read-only filesystem report execution. |
| `scripts/providers/claude_code.py` | Native Claude subscription/Console sign-in routing, explicit model IDs, structured text reports, built-in tools disabled, empty strict MCP config and non-managed hooks disabled. Managed organization policy/hooks can still apply. |
| `scripts/providers/openrouter.py` | Fixed-host HTTPS key/catalog checks, bounded text/image report requests and feature-contained read-only tool loop. No shell/write/MCP tools. API errors are categorized without logging key/response secrets. Redirects are refused. |
| `scripts/providers/credentials.py` | Environment reference or hidden terminal/session-only key input. No plaintext key persistence or visible-input fallback. Prior session credential restored after canceled/failed reconfiguration. |
| `scripts/providers/common.py`, `__init__.py` | Adapter registry, shared report validation, subprocess timeout/interrupt cleanup and status probes. |
| `CLAUDE.md`, `AGENTS.md`, `BOOTSTRAP.md` | Claude entry point and shared instructions; actual workflow rules remain in AGENTS.md. |
| `README.md`, init/team/routing docs | GitHub-first onboarding, provider setup commands, real supported scope and limitations. ZIP remains optional. |
| `tests/test_providers.py`, `tests/test_model_router.py`, `tests/test_workspace.py`, `tests/provider_fixtures.py` | Provider/security/CLI contracts, synthetic native processes/API responses, routing and existing integrity/transfer tests. |

## User flow

Run `./design-workspace init`. It shows or rechecks Codex CLI, Claude Code and OpenRouter. A failed/unknown provider offers setup retry/another provider/exit, not a prompt-only fallback.

Codex delegates sign-in to its native CLI, discovers catalog models and collects supported tier/effort choices. Claude delegates subscription/Console sign-in to its native CLI; user enters aliases/IDs because an account-wide machine-readable catalog was not established. Claude effort stays native default rather than claiming a guessed per-model effort matrix. OpenRouter accepts OPENROUTER_API_KEY or hidden process-memory input, validates key/catalog and configures models. It requires neither native CLI.

Only after coherent setup does init show New, Resume and Change provider/models. A saved profile is reused/rechecked next time. Setup's optional synthetic live test defaults to no and explicitly discloses consumption. Native auth/key/catalog checks do not prove successful inference or model/credit/connector access.

Commands now available:

```sh
./design-workspace providers list
./design-workspace providers setup --provider codex
./design-workspace providers setup --provider claude-code
./design-workspace providers setup --provider openrouter
./design-workspace models status
./design-workspace task plan <feature-id> requirements --provider claude-code --context features/<feature-id>/requirements/00-brief.md
./design-workspace task run <feature-id> requirements --provider openrouter --context features/<feature-id>/requirements/00-brief.md
```

Provider overrides must already be configured and never silently change the saved default. New/Resume scaffolds or restores context; actual analysis runs through explicit task run. It is not an automatic full-stage scheduler.

## Persistence, privacy and project integrity

Ignored workspace.local.json contains a version2 agent_runtime section with a default provider and individual profiles. Existing unrelated keys and version1 Codex model_routing data are preserved. Settings are saved atomically after coherent setup; canceled/failed setup preserves prior settings. An OpenRouter profile stores only an environment/session reference, never the key. OS credential-store support is intentionally unavailable, with no plaintext fallback. Session-only keys require re-entry on a new process; hidden input is refused without a usable terminal.

Task prompts, native events/results, report.md and run.json live under ignored `features/<id>/history/agent-runs/<id>/`. They contain project context and are not public repository content. Model/usage values are native evidence; unknown actual model/cost stays unknown. Worker reports do not change source bytes, stages, deferrals or approvals. The orchestrator still owns integration/checkpoints and final acceptance.

OpenRouter only sends credentials to its fixed approved HTTPS API host, rejects redirects, redacts key echoes and omits error bodies/headers. Its read tool rejects outside-feature paths, symlinks and credential/config paths, with bounded size/request counts. Routine tests use synthetic credentials only.

## Self-test results

Follow-up audit: **46 tests pass** after shared file-boundary, private atomic settings and strict response-validation fixes. The original41-test implementation run below remains historical evidence. See [audit details and continuation](security-and-maintainability-review.md).

`python3 -m unittest discover -s tests -q`: **41 tests passed** on macOS/Python3.13.1.

Tests include:

- Provider selection precedes New/Resume, absence of a Manual path and clean exit without project creation.
- Existing Codex stdio initialization/pagination and report execution through a synthetic executable.
- Claude-only native subprocess setup/report execution with no Codex dependency; explicit Console and native Codex device-code login routes; required worker controls, structured output, actual-model/usage parsing and error/image refusal.
- OpenRouter-only init setup followed by Resume with neither CLI; default setup makes key/catalog checks only, not inference.
- OpenRouter model response execution, usage, actual image payload attachment and bounded feature-read tool calls.
- HTTP401/402/403/429/5xx/redirect categories, network status uncertainty, fixed host/header-only key use and key-echo redaction.
- No-TTY hidden-input refusal; canceled setup preserves prior settings/session key; profiles retain old Codex preferences and support explicit override.
- A real timed-out subprocess is terminated/reaped while retaining partial output; worker source/size/path guards, source/approval preservation, one-attempt default/two-attempt opt-in, no auth/process/schema retry, archive privacy and relocation.

The fake CLI tests execute actual subprocesses and protocol/file handling, but model/account responses are synthetic. OpenRouter HTTP requests are mocked. They do not prove live provider inference, production billing, browser login completion or all managed-policy environments.

Read-only real-session checks: both CLI executables are installed; native Codex login status succeeds; native Claude auth status is unavailable in this session. The real init provider-selection screen was exercised with Exit. No real login flow, API key request, inference or paid smoke test was triggered. Earlier real Codex catalog execution was blocked by this restricted session's state-directory permissions; this is not proof of bad user credentials.

## Remaining boundaries and next verification

- Real account model generation and browser/native sign-in completion need an explicit normal-terminal acceptance test. No production token-saving claim is made.
- Claude image transport is not verified and is blocked; Codex CLI and OpenRouter have implemented image transports, with synthetic payload verification only for OpenRouter.
- No OS secure-store backend; environment/session credentials only.
- Native managed hooks/policies may apply. Codex filesystem sandbox is not external MCP isolation; Claude tool/MCP controls are not a universal OS sandbox. No permission bypass flags or global configuration changes are used.
- Full stage-aware role scheduling, writer-lock coordination, write-enabled Figma agents and automated final handoff remain roadmap work. A report worker returning complete cannot approve a design.
- POSIX subprocess/cleanup fixtures are tested; Windows process-tree/executable behavior remains unverified.
- Context/output/turn limits are not a universal hard total-token/spend ceiling. Raw failure events can contain partial native usage even when run metadata has no successful usage result.

The next acceptance action is to run init in a normal terminal, select the user's own provider and complete native/key setup. Decline the optional live test for a non-inference setup check; explicitly choose a small authorized live task when ready to verify account execution.
