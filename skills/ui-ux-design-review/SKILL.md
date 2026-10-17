---
name: ui-ux-design-review
description: Review actual UI designs against an approved DRD and its approved scope changes, then separately assess UI/UX quality. Use for DRD-to-design compliance checks, main-screen or full-flow design reviews, and correction verification. Produces evidence-backed findings without editing designs; not for writing DRDs, implementing screens, or certifying runtime behavior.
---

# UI/UX Design Review

Review two independent questions: **Does the observed design fulfill the approved DRD?** and **Can people understand and use it well?** Both need evidence. Required fields, visual consistency or a contrast check alone do not complete the review.

## Scope and authority

- Establish the DRD title/revision, approval evidence, approved amendments, current design revision, user roles, surfaces and requested review scope. Read saved decisions, the screen index, deferred-state inventory and earlier findings when present. Do not confuse a generated draft with an approved baseline.
- Use the approved DRD plus recorded approved changes as the acceptance baseline. If the underlying PRD, a later document or the actual design contradicts it, expose the conflict and ask the responsible owner when necessary; do not silently choose a new policy or rewrite the DRD.
- Preserve source terminology and explicitly prescribed copy, fields, roles and rules. Equivalent wording is not automatically a defect unless the DRD requires exact wording or its meaning changes. Treat additional product behavior, restrictions and capabilities as unsupported until justified by an approved source/change.
- In this workspace, Stage 4 follows the recorded variant decision. With a decision pending, continue source/evidence preparation but do not claim Stage 4 complete. A recorded deferral permits a main-screen-only review; it does not waive usability critique of those screens. For standalone requested reviews, record their bounded scope rather than inventing workspace approvals.
- If approval/revision is uncertain, label the review provisional. Identify the missing decision and continue independent analysis; never present provisional coverage as approved compliance.

## Design-read-only role

Read the DRD and inspect design evidence. Do not create/edit/delete Figma nodes, variables, components or prototypes, modify source inputs, install tools, or approve a design. Write the review report and its evidence only to the agreed review destination. The orchestrator owns corrections, decision logs, WIP/checkpoint updates and final acceptance. A single AI can perform those roles in separate passes.

Use the tools and skills actually available in the current AI session. If Figma inspection needs a provider-specific skill, read it first. Use only read operations, including in any JavaScript file-context tool. Skills and file links do not supply authentication or access.

## Review process

### 1. Establish evidence

Record the source/design revisions and what was actually inspected: file/node links, screenshots or exports with their revision/date, node structure, annotations, and any executable prototype or runtime access. Inspect actual screens at a scale sufficient for text and interaction affordances, not only their names or a tiny overview.

Distinguish the existence of a control from its operation. Static screens can establish content, layout and intended affordances; they cannot verify validation, RBAC enforcement, focus, keyboard behavior, screen-reader semantics, email delivery or backend state. An annotation can support intended behavior but cannot prove execution.

If only supplied screenshots or node trees are available, use them within their limits. If no actual design evidence is available, produce source questions and a review plan; mark design coverage unverified. Do not substitute a screen inventory, previous assistant summary or the DRD itself for observed output.

### 2. Build DRD-to-design coverage

Map every material in-scope DRD requirement to its role, field/content, action, flow, rule or state and the actual surface/node evidence. Reuse REQ/FLOW/SCR IDs. If the DRD lacks IDs, assign review-local identifiers tied to its headings; do not modify the source. Group repeated statements without losing distinct obligations.

Classify each item as **verified in static design**, **partially observed**, **missing**, **contradictory**, **deferred by recorded decision**, **unverified**, or **non-UI dependency**. A rule needing runtime proof stays unverified at that level even when its visual representation is correct. Never imply full behavioral verification with a static pass.

Check reverse coverage too: do observed controls, copy and flows introduce behavior or policy the DRD does not support? Separate useful UX proposals from invented product rules. A missing password policy, expiry duration or role catalog remains a dependency; do not choose values to finish the review.

Required but explicitly deferred states remain visible in coverage and limitations, not unexpected omissions or auto-authorized construction work. Deferral must have a recorded decision and scope. A requested but unbuilt prototype is an omission; an unrequested prototype is a verification limitation, not automatically a defect.

### 3. Assess UI/UX quality independently

Use [review dimensions](references/review-dimensions.md) for the applicable screens and journeys. Assess hierarchy, readability, navigation, form usability, table scanning, permissions as represented, action clarity, consequences, feedback and inspectable accessibility. Do not stop after counting fields or checking brand colors.

For each applicable dimension, record **checked with evidence**, **issue found**, **not applicable with reason**, **deferred scope**, or **unverified with reason**. A filled checklist is not evidence by itself. Make screen-specific observations and connect problems to plausible user tasks and outcomes. If a dimension cannot be assessed from available evidence, disclose that gap instead of marking it passed.

Keep product-policy gaps separate from design defects. Treat unrequired filters, search, pagination, bulk actions, new states, extra breakpoints or a preferred modal pattern as optional proposals unless the DRD or demonstrated task evidence makes them necessary. Do not replace the approved visual direction with personal taste.

For a standards-based finding, identify the applicable standard/version and method. Verify normative criteria against primary sources when needed. Calculate contrast from actual foreground/background paints, including transparency; report the pair and method. Do not infer measured ratios from a screenshot or certify overall accessibility from a few samples.

### 4. Report findings and a bounded conclusion

Use [report contract](references/report-contract.md). Give each defect a stable FIND ID, severity, category, DRD/REQ reference (or explicitly no DRD requirement for a usability issue), actual design node/evidence, user impact, specific recommendation and verification limit. Keep optional proposals and unresolved business questions visibly distinct.

Severity reflects impact: **blocker** prevents the agreed core journey or reliable assessment; **high** materially threatens task completion, permissions or consequential actions; **medium** creates meaningful avoidable confusion, errors or access difficulty; **low** is a minor bounded defect. Preferences do not become defects by assigning a severity. Do not report a hypothesis as an observed failure.

Preserve resolved findings and prior evidence. Continue existing IDs; reopen a finding only with evidence of regression. Label what the reviewer observed versus inferred and which decisions need an owner.

Conclude **review incomplete**, **changes required**, or **ready for user acceptance within the stated scope**. Readiness requires DRD coverage and all applicable UX dimensions to be assessed at the promised evidence level, with no undispositioned material issues or hidden review gaps. Unknown runtime behavior must remain a limitation. The user still owns final acceptance; main-screen readiness is not full feature readiness.

## Correction verification

After the orchestrator corrects an existing finding, inspect the changed nodes/screens again and check nearby regressions. Close it only with new evidence matching its acceptance condition. Recheck affected DRD coverage and usability dimensions; do not repeat unaffected tests without reason. The reviewer does not perform the fixes. In this workspace, the orchestrator follows the two-round automatic correction limit and returns new state/scope requests to the appropriate gate.

## Output and portability

Default workspace report: `features/<feature-id>/reviews/06-design-review.md`; keep evidence under that feature's `reviews/` folder. Reuse the existing report when continuing a run and preserve previous revisions through the orchestrator. For standalone reviews, use the user-agreed output path. Write no unrelated project records.

This skill is readable Markdown and does not require a particular AI provider or Figma connector name. Missing connectors reduce what can be verified. Report that explicitly and continue source/evidence analysis when useful. No model, external service, renderer, credential or approval is bundled with the skill.
