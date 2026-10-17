# Design review checklist

Use only checks relevant to the feature and approved review scope.

Use `skills/ui-ux-design-review/SKILL.md` at Stage 4. Review both approved-DRD compliance and UI/UX quality; neither replaces the other.

- Traceability from source requirements to flows and screens.
- Every material approved DRD obligation has observed evidence and a coverage status; unsupported design additions are identified separately.
- Proposed policy and IA clearly distinguished from facts.
- Entry/exit paths, handoffs, permissions, and action visibility.
- Field behavior, validation, feedback, duplicate-action prevention, recovery.
- Required states identified; built and deferred variants distinguished.
- Actual Figma inspected; frame/node evidence recorded.
- Approved components/tokens, content hierarchy, terminology, masking.
- Screen-specific purpose/hierarchy, navigation, form grouping/guidance, table scanning, action clarity, consequential-action context and cross-screen coherence.
- Each applicable usability dimension records evidence, issue, justified not-applicable, deferred scope or an explicit verification gap; do not mark it passed from an inventory alone.
- Accessibility and responsive design inspected to available evidence.
- Prototype paths verified where requested and inspectable.
- Findings have severity, evidence, impacted IDs/nodes, and correction.
- Remaining dependencies and limitations recorded for final acceptance.

Never infer full state coverage from main screens alone or runtime accessibility from static inspection.
Do not recommend final acceptance while relevant review dimensions or material evidence remain missing. Separate defects, optional UX proposals, product-policy dependencies and user-approved deferrals. The review skill remains read-only for design canvases; fixes belong to the orchestrator.
