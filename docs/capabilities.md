# CLI capability checks

Setup detected codex-cli 0.160.0. This confirms the executable is present, not a successful authenticated feature run.

On the first real feature run, inspect the session's available skills and tools. Confirm relevant source files are readable and Figma read/write tools and authentication are actually available before Stage 3. Desktop tool availability does not establish CLI availability.

For a missing workflow skill: inspect candidates and suggest them; if none fits, create a project-local skill with skill-creator and validate it. For an absent connector or credentials: state the missing capability and required setup. Do not store credentials in this workspace or silently change global configuration.

The workspace works for requirements and DRD planning without Figma access. Each teammate verifies Figma in their own session; another person's completed feature does not verify their access.

The provider-independent helper requires Python 3.10+ and no third-party packages. `doctor` checks local files, `resume` prints prompts, and `check` verifies paths/hashes. They do not test authentication, skill discovery, fonts, rendering, Figma access or instruction following. Initial CLI detection above is historical, not a dependency on Codex or that version. See `docs/team-setup.md`.

Routed bounded worker support is now implemented through the local Codex app-server/exec interfaces. Model discovery is not an inference/access guarantee; settings stay in workspace.local.json. Live discovery in the restricted authoring session could not initialize Codex state. See model-routing.md and model-routing-validation.md for current scope and tests.

## Three-provider update

Provider-first setup and explicit report workers now support Codex CLI, Claude Code and OpenRouter. Historical Codex-only notes above are superseded by docs/provider-implementation-report.md. Claude image transport and OS secure-store integration are not implemented; no successful live model inference is claimed from synthetic tests.
