# Resume and change control

Read `status.md`, `decisions.md`, the current accepted artifacts, and only relevant source material. Reconcile saved state with actual files/Figma after interruption. Check uncertain tool outcomes before repeating a write.

Status states: ready, running, awaiting-user, blocked, complete. Use blocked here for a feature dependency, not as a claim about any separate platform goal status.

Save after accepted output, user decision, material revision, or a recoverable interruption. Record current stage, accepted input/output revisions, last completed work, unverified active work, pending decisions, variant scope, and next action.

For changes: record the request and source; map affected REQ/FLOW/SCR IDs; mark dependent outputs needs-recheck; preserve an identifiable accepted baseline; update affected work only; repeat relevant review and approvals. A new persona, core journey, approval model, or financial policy can require re-baselining. Follow the local DRD skill for its major-change approval rules.

Use existing Git only if appropriate; do not assume it exists or auto-commit. Preserve changed approved artifacts in a feature-local `history/` folder when needed, and identify their versions. Never overwrite source inputs. If a source changes externally, record the revision mismatch and assess impact.

Do not reuse stable IDs for different meanings. Mark retired scope explicitly. Keep waiting decisions pending; elapsed time is not approval. On resume at C2, ask the variant decision rather than rebuilding main screens or entering review.
