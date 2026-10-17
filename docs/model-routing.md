# Model routing and bounded provider workers

Configure via provider-first init or directly:

```sh
./design-workspace providers list
./design-workspace providers setup --provider codex
./design-workspace providers setup --provider claude-code
./design-workspace providers setup --provider openrouter
./design-workspace models status
```

You need only the provider you choose. Setup checks native CLI auth or OpenRouter key readiness, configures Economy/Balanced/Quality and light/standard/strong tiers, and asks whether one higher-tier escalation is permitted. Default Balanced and one attempt. Optional live setup tests explicitly disclose allowance/credit use and default to no inference.

Codex models/efforts come from the installed app-server catalog. Claude model IDs/aliases are entered explicitly because account-wide machine-readable discovery is not established; effort stays native default instead of inventing a per-model effort matrix. OpenRouter validates the key and fetches model capability metadata; unsupported effort is not guessed. Model/catalog/auth readiness are distinct from proven successful generation, pricing and tool access.

| Kind | Economy | Balanced | Quality |
| --- | --- | --- | --- |
| extract/summarize | light | light | standard |
| requirements | light | standard | strong |
| design | standard | strong | strong |
| review/visual-review | strong | strong | strong |

These are user-defined tiers, not automatic price rankings or quality guarantees. Python handles deterministic file/scaffold/hash/package work with no model.

Settings live in ignored workspace.local.json: version2 agent_runtime contains the default provider and separate profiles. Legacy version1 Codex model_routing remains readable and is retained unchanged as data when a new provider profile is saved. Unrelated settings are preserved atomically. No API keys or native login files are copied into configuration. OpenRouter stores only an environment/session reference; OS credential-store persistence is not implemented.

## Plan/run

```sh
./design-workspace task plan customer-portal requirements --context features/customer-portal/requirements/00-brief.md
./design-workspace task run customer-portal requirements --context features/customer-portal/requirements/00-brief.md
./design-workspace task run customer-portal review --provider claude-code --context features/customer-portal/sources/approved-drd.md
```

Replace example IDs/files. An explicit provider override must already be configured and does not change the saved default. Never retry on another provider automatically. Plan checks configuration/checkpoint and prints routing/evidence hashes without authentication/inference. Run checks actual provider readiness, selects the model and records the outcome. Existing source/approval gates remain authoritative.

Supplied source evidence includes status/decisions plus up to10 explicit UTF-8 context files from the selected feature. Default source-text limit30,000 characters; workflow/role instructions are compiled separately so tools-disabled providers can follow them. At most5 feature images. Codex uses CLI image arguments; OpenRouter attaches base64 image content for catalog-confirmed image models (supported formats, maximum5MiB each). Claude visual input is unverified and blocked explicitly.

Provider execution controls differ: Codex has read-only filesystem sandbox, not guaranteed external MCP isolation; Claude disables built-in tools, uses strict empty MCP config and disables non-managed hooks while managed policy can apply; OpenRouter exposes only supplied context plus a feature-contained read tool if the model supports tools. OpenRouter has at most4 model responses/3 read requests per attempt, another bounded30k-byte read allowance and2048 maximum output tokens per response. No shell, arbitrary tool, file write or MCP operation is exposed through that adapter. File paths cannot escape the feature; credential/config paths and symlinks are rejected.

These limits are not a universal hard total-token/spend ceiling. Images, native provider instructions, output/reasoning and repeated tool context add usage. No percentage saving is claimed without a benchmark.

## Results, escalation and limitations

Each invocation saves prompt/schema, per-attempt output/events, report.md and run.json under ignored `features/<id>/history/agent-runs/<id>/`. Metadata includes provider, requested/actual model when supplied, native usage, attempts, timing, input/image hashes and tool reads. Unknown usage/cost stays null; provider estimates are not necessarily subscription charges/invoices. Keys are never logged by the API client; it uses a fixed HTTPS host, refuses redirects and sanitizes responses/errors.

Default one attempt. With prior opt-in, an explicit needs-escalation report can request one next-tier retry, maximum two total. No identical model+effort repeat and no retry from strongest tier. Auth/network/process/schema failures do not automatically retry. CLI timeout/interrupt terminates the worker process group on POSIX and records partial outcomes; Windows process-tree behavior is not verified.

Worker completion means a validated report, not acceptance. Reports do not edit projects/designs, advance stages or grant approval. The orchestrator reviews/integrates accepted artifacts and updates WIP/checkpoint. No role scheduler or automated Figma writer is claimed.

See [implementation report](provider-implementation-report.md) for tests, actual live-verification limits and exact file locations, [Codex app-server](https://learn.chatgpt.com/docs/app-server), [Claude CLI](https://code.claude.com/docs/en/cli-reference), and [OpenRouter tool calling](https://openrouter.ai/docs/guides/features/tool-calling) for native contracts.
