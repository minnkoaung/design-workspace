# Tool progress, security review and continuation

Date: 2026-10-17. Scope: reusable CLI code and documentation. Changes are local; publication is pending. This is a focused code review with regression tests, not a security certification.

## Current progress

| Area | Actual status |
| --- | --- |
| Local project memory | New/Resume, WIP, local source snapshots, schema3 checkpoints, integrity checks and selective transfer implemented. Saved files are the recovery source of truth. |
| Startup | Codex CLI / Claude Code / OpenRouter selection precedes New/Resume. No Manual workflow option. Each teammate supplies authentication. |
| Model routing | User-assigned light/standard/strong tiers, three routing policies, strong review, explicit provider override, default one attempt and optional bounded escalation implemented. No invented prices or token savings. |
| Agent execution | Explicit bounded report workers implemented for all three adapters. Workers do not grant approvals or advance stages. |
| Full orchestration | Automatic stage-aware role scheduling, dependency handling, writer locks and write-enabled design execution remain unfinished. Init itself does not start an autonomous project run. |
| Provider acceptance | Fixture execution passes. Real account generation, real image interpretation and Windows process behavior remain unverified. Claude image input is blocked. |
| Distribution | GitHub is the primary path; ZIP is optional and static. Current source changes have not been committed/pushed by this session. |

## Findings corrected

| Finding | Change and location | Evidence |
| --- | --- | --- |
| Explicit context lacked the credential-file policy used by the API read tool. | `scripts/local_io.py` now shares the policy across `model_router.build_prompt` and `providers/openrouter.read_tool`: reject credential/config filenames, environment files, private provider directories and key extensions. Existing containment/symlink guards remain. | Regression tests exercise both routes against synthetic sensitive files, including mixed-case extensions and nested SSH material. |
| Whole-file reads allocated content before enforcing the size limit; content and hash came from separate reads. | Shared bounded binary read decodes and hashes the same bytes. Explicit text remains character-limited; API tool reads remain byte-limited. Compiled instruction files are individually bounded. | Existing over-budget tests pass alongside context/tool tests. |
| Settings writers duplicated logic, used default file permissions and could delete another writer's temporary file after an exclusive-open race. | Shared atomic writer uses exclusive creation, owner-only POSIX permissions, flush/fsync and replacement. Cleanup starts only after ownership is obtained. New report-run directories use owner-only POSIX permissions. | Tests verify settings mode0600 and that a competing temporary file and prior settings survive a refused write. |
| Malformed nested settings could produce attribute/type errors; booleans could be accepted as numeric limits. | Validate provider/version/mode/tier shapes, effort types and exact integer limits before execution. | Invalid lists, null tiers and boolean limits fail as configuration errors. |
| Worker output accepted extra fields despite the declared strict schema; malformed API tool calls could cause attribute errors. | Enforce exact report keys and status type, validate tool-call envelopes/arguments, reject non-object Claude results. | Extra-field, invalid-status and malformed-tool regressions pass; failed output does not trigger automatic retries. |
| Roadmap still described Claude workers as unimplemented and cited the old23-test baseline. | Updated `docs/provider-adapters-plan.md`, linked this report from README and the implementation report. | Current code/plan now distinguish local implementation from live acceptance and the unfinished scheduler. |

The filename policy prevents common accidental disclosure; it is not content-based secret detection. A secret placed in an ordinary evidence document can still be sent. Use only relevant evidence. Native CLI workers retain their provider's policy boundary: Codex read-only filesystem access is not external MCP isolation; Claude managed policy can still apply. OpenRouter exposes only the bounded feature-read tool.

## Code structure and human readability

- `workspace.py`: commands, project files, checkpoints and distribution.
- `agent_runtime.py`: provider-first setup, profile selection and native authentication handoff.
- `model_router.py`: task-to-tier policy, selected context, bounded attempts and run records.
- `providers/`: provider-specific authentication, catalog, invocation and response handling.
- `local_io.py`: shared settings-write and evidence-read boundaries with short documented helpers.
- `tests/`: synthetic provider contracts, real local subprocess fixtures, file privacy and recovery regressions.

Keep provider mechanics behind their adapters. Share security boundaries instead of copying them. Use argument lists for subprocesses, no shell command interpolation, fixed HTTPS API endpoints, no automatic provider fallback, and explicit errors for unsupported capabilities. Keep credentials outside settings/Git and synthetic in tests. Preserve evidence and approvals separately from worker completion. These are maintenance rules for future changes, not a claim that every provider environment is equivalent.

## Verification

`python3 -m unittest discover -s tests -q`: **46 tests passed**. Five new regression tests cover settings ownership/permissions, malformed routing, sensitive-file parity, strict report fields and malformed API tool calls. Existing fake-CLI subprocess, mocked API, timeout, retry, privacy and relocation tests also pass.

No real login flow, API key collection, model generation or paid smoke test was run. No project source, design, approval or deferred-state decision was changed. Git metadata remains unwritable in this session, so publication requires the user's normal terminal.

## Exact continuation

1. Review and publish the tested reusable source changes from a normal terminal, excluding local project work, settings and credentials. Use the scope and explicit staging guidance in `docs/repository-scope.md`.
2. Complete a small normal-terminal acceptance run with the user's own chosen provider. Setup may be checked without inference; a live generation test must be explicitly selected. Record actual version/model/usage and capability limits without credentials. Do not require every teammate to configure all three providers.
3. Build the next orchestration milestone: persistent task/dependency records, stage/approval gate checks, ownership locks, interruption/resume semantics and bounded scheduling. Start with one worker at a time and fixture-test interruption, stale checkpoints and writer collisions before enabling parallelism.
4. Add verified visual capability and write-enabled design execution only where the actual provider/connector can enforce the promised scope. Keep human approval gates and existing project decisions intact.

To resume development, read `AGENTS.md`, this report, `docs/provider-adapters-plan.md` and the relevant code/tests. Reconcile Git status and current test results before editing. For a design feature, use its own WIP/status/decisions/checkpoint instead of this tool-development report.
