# UI/UX Design Review skill validation — 2026-10-16

Skill: `skills/ui-ux-design-review/SKILL.md`. Prepared using skill-creator guidance. No live project review was performed during skill preparation.

## Structural checks

Passed YAML parsing with Ruby `YAML.safe_load` for SKILL.md frontmatter and optional agents/openai.yaml. Checked skill name/description, UI blurb length, default prompt invocation, implicit-selection setting, local reference links and unfinished-scaffold absence. Both focused references exist.

The skill-creator Python `quick_validate.py` was attempted but could not execute because its PyYAML dependency is absent. The Ruby parser check is an alternative structural check, not a successful run of that official validator. No dependency installation or global settings change was made; Ruby/PyYAML are not runtime requirements for reading this skill.

## Independent behavioral exercise

An independent agent received the skill, a synthetic approved DRD, recorded scope/deferral decisions, prior resolved findings and serialized design-node evidence. It was given no expected answer or suspected-defect list. It could write only a report in an isolated temporary fixture folder and could not call external systems or edit inputs/workspace records.

The resulting report identified all five intended DRD mismatches: missing create-form Mobile Number, unsupported 24-hour expiry promise, editable email contrary to the approved release, missing reset destination email, and reset visibility intent conflicting with the admin-only rule. It separately identified the email-column clipping configuration as a usability finding, distinguishing observed configuration from inferred rendered impact.

It preserved FIND-001/FIND-002 as resolved and continued from FIND-003; mapped REQ-001–007; checked reverse coverage; treated approved state deferral as a limitation rather than an unexpected omission; did not demand an unrequested prototype; and did not invent a role catalog, expiry policy, measured contrast or runtime access failure. Its conclusion was changes required with visual/interaction review incomplete, not final readiness.

Fixture inputs are preserved under `tests/fixtures/ui-ux-design-review/`; the report is `docs/validation/ui-ux-design-review-exercise.md`. This is a behavioral exercise, not a guarantee that every future review will find every defect. No connector, actual Figma rendering or live product behavior was verified.

## Workflow and distribution checks

AGENTS.md explicitly routes Stage 4 to the skill, overriding older abbreviated review references without modifying protected `.agents/` files. The workspace checklist requires DRD coverage and independent usability observations. The reviewer is read-only for design canvases; the orchestrator owns authorized corrections and persistent stage/approval records.

All eight local CLI tests passed after adding `skills/` to the starter allowlist and adding the reviewer to prerequisite checks. The package test verifies the review skill is included. Updated starter archive is `dist/team-starter.zip`; the previous archive is retained under `dist/history/`. Teammates without native skill discovery read the path explicitly. Real AI clients, Figma access, rendering and runtime verification remain session-specific.
