# Stage contracts

Read the current stage and its dependencies. Gates are human decisions. Prior explicit authorization remains valid within scope; silence does not approve anything.

## Stage 0 — Intake and plan

Read brief/references, identify source authority and source revision, scope, deliverables, missing information, role assignments, tool/skill gaps, and dependencies. Create `00-brief.md`, `01-run-plan.md`, `status.md`, and `decisions.md` when useful. Ask grouped clarifications only after reading inputs.

## Stage 1 — Requirements

Create `02-requirements.md`: stable REQ IDs, source locations, users/roles, goals, business rules, permissions, preconditions, completion, exceptions, exclusions, dependencies, and unanswered decisions. Separate supported facts from proposals. Undefined product policy is not a UX assumption that agents can approve.

Gate A: user approves material requirements/scope decisions. Work not dependent on unresolved decisions can continue. Record the approval's artifact revision and scope.

## Stage 2 — UX and screen plan / DRD

UX Strategist defines FLOW IDs, journeys, IA, entry/exit, handoffs, success and recovery. Screen Planner defines SCR IDs, access, content and fields, controls, permissions, transitions, validation, relevant loading/empty/error/pending/success states, responsive behavior, accessibility, and observable acceptance checks. Link each surface to requirements and label proposed architecture.

For CTZPay, follow the local DRD skill and produce `03-drd.md`. Keep supporting analysis compact. Check coverage and unsupported rules in `04-drd-review.md`.

Gate B: user approves DRD/screen scope for Figma. Ask ownership once before DRD generation as required by the local skill. Word creation requires its own explicit approval. DRD approval does not approve generating variants.

## Stage 3A — Main screens only

Verify CLI-accessible Figma tools, file access, approved design foundations, components, tokens, references, and assets. Reuse applicable Figma skills. If unavailable, report the actual dependency and continue independent work; do not claim Figma output.

Define the smallest distinct main-screen set representing the approved primary journey. A necessary primary-path dialog may be included if identified in that approved set. Create only default/primary screen states. Do not automatically create alternate screen states, breakpoint copies, role/theme variants, or new component variants. Reusing an existing component variant is allowed.

Gate C1: if introducing a new visual direction, create one representative screen and get approval before expanding it. Skip for direct application of approved foundations without material deviation.

Complete only the approved main screens, then present their links/previews and a compact variant proposal: affected screen, purpose, requirement/risk covered, and estimated additional frames. Document every required state in the DRD even if not built yet.

## Gate C2 — Mandatory variant decision

Ask the user to approve all variants, select particular variants, or defer variants and review main screens only. Do not create variants or enter Stage 4 while the decision is pending. General requests to continue do not waive this gate. Record the explicit choice, variant groups, artifact revision, and review scope.

## Stage 3B — Approved variants only

Build selected variants only. Do not replace explicitly requested frames with annotations. With deferral, preserve the unbuilt-state inventory and move to a limited review. Keep `05-design-index.md` with SCR IDs, links, revision context, and each variant's status: planned, awaiting approval, approved to build, built, reviewed, or deferred.

## Stage 4 — Review and revision

Enter only after C2 resolves and approved variant work finishes. Review actual Figma output against source, DRD, and approved review scope. Check access/navigation, permissions, state coverage, recovery, content, design foundations, accessibility, responsive behavior, and requested prototype paths.

Create `06-design-review.md`. Findings need FIND ID, severity (blocker/high/medium/low), evidence, affected requirement/screen/node, impact, and requested correction. Distinguish defects from optional preferences and planned deferrals. Static inspection cannot establish runtime or assistive-technology behavior.

Fix affected work only, up to two automatic rounds, then escalate. New variants outside the approved scope return to C2. Fixing already approved variants does not require repeated approval. Deferred required states remain limitations; do not claim full coverage.

## Stage 5 — Final approval and handoff

Gate D: user accepts final design and explicitly accepts/defers remaining material findings. A main-screen-only package can be accepted as bounded scope, not as a fully implementation-ready feature.

Create `07-handoff.md` with approved version references, screen/state inventory, Figma links, interactions, review outcome, deferred findings, dependencies, and limitations. Maintain `change-log.md`. Produce requested exports only; follow relevant document/PDF skills and actual verification requirements.

A polished screen or completed agent response is insufficient for completion. Full delivery requires traceability, required states/interactions, actual design review, accurate links, and resolved or explicitly dispositioned findings.
