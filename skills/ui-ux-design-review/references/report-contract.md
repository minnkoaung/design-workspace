# Review report contract

Keep the report useful for the designer and decision owner. Do not generate a large repetitive matrix when a concise coverage table and screen observations preserve the same evidence.

## Baseline and conclusion

Record DRD title/revision and approval evidence; approved changes/deferrals; design file/node/revision; roles, surface and languages; review scope; evidence actually inspected; and missing evidence. Lead with the bounded conclusion and important findings, without calling a provisional or partial review complete.

## DRD compliance coverage

| Requirement / DRD section | Expected design obligation | SCR/node and observed evidence | Coverage status / limitation |
| --- | --- | --- | --- |

Account for every material obligation and reverse-check unsupported additions. Use review-local IDs when necessary, retaining source headings. Non-UI and runtime-only rules remain dependencies/unverified at that level. Preserve recorded deferrals separately.

## UI/UX quality observations

For each relevant dimension from review-dimensions.md, state what was checked, affected screens/evidence, observation, and outcome/limit. Separate DRD coverage from usability quality. Example: all nine required table columns can be present while actual widths make email addresses unreadable. That is a usability issue even though the column requirement is represented.

## Findings

For each finding include:

- Stable FIND ID; severity; status; category: DRD noncompliance, UI/UX usability, accessibility, or design-system defect.
- DRD section/REQ/FLOW/SCR and actual node, screenshot/export reference or observed interaction evidence. A usability defect may have no explicit DRD criterion; say so and cite the user's task rather than inventing one.
- Expected versus observed behavior/content where applicable. Separate factual observation from inference or hypothesis.
- Concrete user impact, actionable correction and observable verification condition.
- Decision owner when a policy/scope decision is needed; do not invent a named owner.
- Verification limits and whether reinspection found a regression or closed the original finding.

Keep optional UX proposals, unresolved product questions, planned deferrals and unverified runtime behaviors outside the defect list unless there is a separate observed defect. They must not disappear from limitations just because they are not defects.

## Completion and handoff

Report coverage limits, open/resolved findings, and exact next action. Choose a bounded conclusion:

- **Review incomplete:** required evidence, source authority or an applicable review dimension is still missing. State what can be concluded so far.
- **Changes required:** evidence supports defects requiring correction or explicit disposition before acceptance.
- **Ready for user acceptance within stated scope:** the promised static/prototype review is complete, material findings are corrected or explicitly dispositioned, and remaining limitations/deferrals are visible. Do not imply user acceptance already happened.

If reporting both defects and evidence gaps, include both conditions; never use a readiness label to hide incomplete review work. Source policy conflicts need resolution by the appropriate owner. The orchestrator, not this reviewer, updates stage/checkpoint/WIP and performs corrections.
