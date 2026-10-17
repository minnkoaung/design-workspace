# Reusable tool repository

Track the CLI launcher and Python helper, workspace instructions, generic orchestration/review skills, templates, standards, onboarding documentation and synthetic fixtures/tests.

Keep local project work out of Git: `features/`, `WIP/`, generated `dist/` archives, personal provider settings/credentials, project-specific copied converters/brand assets and local pilot/setup notes are ignored. Existing local files are preserved; ignoring does not delete them. The clean starter also excludes the local-only skill and notes, even when they exist in the author's workspace.

Cloning retrieves the tool, not project history or client deliverables. New feature/WIP directories are created by `init` or `new` when needed. Check an intended commit with `git diff --cached --stat` and `git diff --cached --name-only`; do not force-add project folders.

To share a project deliberately, use the separately documented `pack --include-feature <id>` flow and review the selected content before transfer. A selected project transfer is distinct from publishing the reusable tool repository.

No external AI/Figma connectors, account configuration or credentials are supplied. Each teammate connects their own AI tool and permitted services. No license grant for optional copied project assets is implied.

## First commit and push

Run these in your own terminal from the workspace after selecting the destination repository. The GitHub repository should be empty; reconcile any existing history before pushing.

```sh
git init -b main
git add .gitignore AGENTS.md BOOTSTRAP.md README.md design-workspace scripts tests skills standards templates docs/init-cli.md docs/team-setup.md docs/capabilities.md docs/review-skill-validation.md docs/repository-scope.md docs/validation .agents/skills/design-workflow
git diff --cached --stat
git diff --cached --name-only
git commit -m "Add portable design workspace CLI and reusable workflow skills"
git remote add origin <your-github-repository-url>
git push -u origin main
```

Review the staged paths before committing: no `features/`, `WIP/`, `dist/`, project-specific converter/assets or local pilot notes should appear. Use your own authenticated GitHub/SSH credentials. For GitHub CLI authentication, run `gh auth login -h github.com` interactively in your terminal if needed; do not paste credentials into chat or this repository.
