> Historical Codex-only implementation record. Current multi-provider scope/tests: [provider implementation report](provider-implementation-report.md).

# Model-routing implementation and verification — 2026-10-17

## Delivered and locations

- `scripts/model_router.py`: Codex app-server initialization and paginated model discovery; supported effort/image metadata; interactive local configuration; Economy/Balanced/Quality task selection; context/image preflight; real `codex exec` adapter with read-only filesystem sandbox, structured reports, bounded escalation, timeout and per-run evidence.
- `scripts/workspace.py`: `models list/setup/status`, `task plan/run` integration, init option 3, resume routing status and required router prerequisite.
- `AGENTS.md`: mandatory routing setup for delegated CLI tasks, model-selection/usage/worker boundaries, orchestrator ownership and no invented savings/approvals.
- `.gitignore`: local settings temporary file excluded alongside settings and all feature/WIP work.
- `tests/test_model_router.py`: discovery/worker protocol fixtures, selection/setup, local preference preservation, bounded context, image/effort/retirement checks, symlink refusal, opt-in escalation, transport/invalid-output failures and usage records.
- `tests/test_workspace.py`: CLI routing preflight and package exclusions, alongside existing intake/transfer/integrity coverage.
- `docs/model-routing.md`, README, bootstrap/init/team/capability/repository documentation: commands, policy, output paths, ownership and limitations.

Settings will be created at ignored `workspace.local.json` only when the user completes successful setup. No real account model IDs were guessed or selected during development. Actual task logs/results go under ignored `features/<id>/history/agent-runs/<timestamp-id>/`, not the reusable GitHub source. No live project task was run or feature approval changed by this maintenance.

## Verification

`python3 -m unittest discover -s tests -v`: **23 tests passed** on the development macOS/Python environment.

The fixture executable simulates the Codex subprocess over real stdio: initialize/initialized handshake, two model-list pages, worker result files, JSONL usage events, failure and explicit escalation. It rejects unexpected protocol calls. This verifies the adapter's process/argument/file/event handling against the fixture contract; it is not live provider evidence. Routing tests confirm default one-attempt behavior and maximum two-attempt opt-in escalation. Existing tests verify relocation, original-source integrity and clean starter exclusions; local routing settings and temporary settings are excluded.

Native POSIX fake-executable and symlink tests are skipped on Windows; Python/file routing is designed to be portable but Windows process behavior is not verified here. No inference price or token savings benchmark was measured.

Live `./design-workspace models list` was attempted. This restricted authoring session could not initialize the installed Codex state runtime; direct CLI diagnostics confirmed its SQLite state directory was not writable. No model catalog was returned and no inference was started. Provider configuration/credentials were not copied or changed, and this failure was not bypassed with a different credential/state directory. Model access, actual output-schema behavior, fonts/connectors and real usage must be verified from a normal authenticated terminal.

## User acceptance check in normal terminal

```sh
./design-workspace models list
./design-workspace models setup
./design-workspace models status
./design-workspace task plan <feature-id> requirements --context features/<feature-id>/requirements/00-brief.md
```

Replace placeholders with an existing valid feature. Setup shows the user's real catalog and collects model/effort choices. Plan invokes no inference. To test execution, explicitly use `task run` with a small authorized task/context; inspect run.json, report and provider usage. A real worker consumes the user's allowance/billing and inherits their permitted tool availability.

## Practical scope

This delivers model-aware bounded analysis workers, not an automatic end-to-end design-agent scheduler. Workers produce reports; the orchestrator still integrates changes, registers evidence/checkpoints and enforces existing stage/variant/final-acceptance gates. Read-only filesystem mode does not enforce external-service tool isolation. Character limits and small prompts reduce supplied context but are not hard total-token/spend ceilings. Unknown actual model/usage/cost stays unknown; model tier names do not prove pricing or quality. Existing interactive chats do not switch models automatically.

## Follow-up — GitHub onboarding and missing Codex

README now leads with GitHub clone/pull and treats ZIPs as optional offline/project-transfer artifacts. Init detects absent Codex on PATH, displays that New/Resume remains available, labels option3 as requiring Codex, and returns to the menu after explaining a disabled model choice. Resume prints a portable AI prompt; doctor reports absent Codex without failing local prerequisites. Direct discovery/worker execution fails before starting a subprocess, with no automatic installation or provider fallback. Three missing-Codex tests added; current suite23 passes. Other-provider automatic execution remains unimplemented. These changes are local until committed/pushed.
