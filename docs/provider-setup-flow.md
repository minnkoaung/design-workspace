# Provider-first setup flow: Codex, Claude Code and OpenRouter

Date: 2026-10-17. Status: setup/report-worker flows implemented; this document remains the design baseline. See [implementation report](provider-implementation-report.md) for tested support and remaining limitations.

## Confirmed user requirements

The CLI is an agent orchestration tool. At startup it must detect/configure a working execution provider, with three choices: Codex CLI, Claude Code and OpenRouter. Provider selection comes before New/Resume. Remove the proposed Manual workflow option entirely: printing prompts without agent execution is not an orchestration mode.

No configured provider means workflow execution cannot start. Offer provider setup, retry, another provider or exit. Local maintenance commands such as list/check/doctor may remain available independently; they are not a substitute workflow mode. Provider choice is saved per teammate/checkout and rechecked on later starts. Existing sources, stages, approvals and state deferrals remain unchanged when providers change.

## Entry and shared sequence

```text
./design-workspace init

Choose your AI execution provider:
1. Codex CLI     [installed / authentication not checked]
2. Claude Code   [not installed]
3. OpenRouter    [connection not configured]
0. Exit
```

Statuses are illustrative. Detect executables/version without treating them as authenticated. For OpenRouter inspect only configured credential-reference presence or the named environment variable, not unrelated files/secrets. OpenRouter is an API connection, not a CLI executable to detect.

Provider choice → prerequisite check → authentication/connection setup → non-inference validation → model/effort routing → optional disclosed live test → save nonsecret preferences → New/Resume menu.

```text
Provider: <selected provider>
Authentication: validated / unknown / failed
Model configuration: configured
Live task: not tested / verified

1. New project / feature
2. Resume existing feature
3. Change provider or models
0. Exit
```

On subsequent starts show the saved provider and recheck readiness. Reuse valid settings without asking every question again. An unavailable/revoked provider leads back to setup/selection; do not automatically send project data to another service. A provider may be configured without an optional inference smoke test; the first real task must then verify actual model access. Do not label it live-verified early.

## 1. Codex CLI branch

1. Detect `codex` and inspect its version/required features. If missing, explain the prerequisite and offer official installation instructions, Check again, Choose another provider, or Exit. Do not install automatically.
2. Check authentication using `codex login status`, with a timeout. Normalize the result without copying credential files or persisting raw sensitive output. A local status check is not a network/model-access guarantee.
3. If unauthenticated, ask whether to launch the native sign-in flow now. On selection, delegate browser sign-in to `codex login`; offer supported device-code sign-in when appropriate. Leave account/token handling to Codex. Do not request a ChatGPT password or copy another person's login.
4. Recheck status; query the installed app-server model catalog. Discovery failure exposes the reason and offers Retry/Choose another provider/Exit. Do not silently substitute a guessed model list.
5. Ask once for Economy/Balanced/Quality, tier models, native supported efforts and maximum retry policy. Preserve existing choices when reconfiguring.
6. Offer an optional small live task, clearly stating it can consume the user's allowance/billing. Default not to run the test. A declined test is not Manual mode: the provider remains selected for real tasks with access still unverified.
7. Save nonsecret provider/model settings and continue to New/Resume. Existing Codex authentication stays owned by its CLI.

Local help confirms `codex login`, `login status` and `--device-auth`. Authentication behavior must be reconciled with the installed version and policy. [Official Codex authentication](https://learn.chatgpt.com/docs/auth).

## 2. Claude Code branch

1. Detect `claude`, inspect version and confirm required print/output/tool controls. Installed alone is insufficient. Missing/incompatible CLI offers instructions, Check again, Choose another provider or Exit.
2. Use native `claude auth status` and parse only readiness/auth-method fields needed for setup. Never copy private CLI state or save an auth response blob.
3. If unauthenticated, ask which native login route the user intends: Claude subscription or Anthropic Console/API billing. Make the distinction visible before sign-in. Delegate to the applicable native `claude auth login` flow; Console uses the supported `--console` option. Browser/SSO interaction belongs to the provider CLI. Do not ask for a Claude account password or unrelated OpenRouter key.
4. Recheck authentication. A successful sign-in does not establish every model or connector permission.
5. Configure model tiers/effort. Use a verified discovery mechanism if available; otherwise explicitly ask the user for model aliases/IDs and label them user-configured/access-unverified. Do not present a fabricated catalog or imply aliases always resolve to one fixed model.
6. Offer the same optional disclosed live test. Parse native model/usage evidence, surface remapping, and reject missing required capabilities instead of silently degrading.
7. Save nonsecret settings, keep authentication under Claude Code, and enter New/Resume. Do not require Codex for this branch.

Local Claude Code2.1.287 help confirms the native auth/status/login routes; authentication itself was not tested during planning. [Official Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## 3. OpenRouter branch

1. Explain: this connects the orchestrator's own API/agent adapter; no Codex or Claude Code installation is required. OpenRouter model access does not automatically supply local tools, Figma access or an agent loop.
2. Ask how to supply the key:
   - Use the existing `OPENROUTER_API_KEY` environment variable, if present. Show only that it is present, never its value.
   - Enter an API key through hidden terminal input. Example prompt: `OpenRouter API key (hidden; session only):`. Do not echo it, put it in command arguments/shell history, or ask for it in chat. If secure terminal input is unavailable, refuse visible input and explain the environment-variable route.
   - Back/Choose another provider or Exit.
3. Default newly entered keys to memory for this process only. If persistence is requested, offer an OS credential-store backend only when implemented and available. Save only its reference in local settings. If secure storage is unavailable, keep session-only/environment mode; never fall back to plaintext settings, .env, project files, logs or Git. Do not modify shell profiles/global configuration. A session-only key must be requested again on a fresh process unless the user supplies an environment/store reference.
4. Validate via the current-key endpoint with a bounded HTTPS request, then fetch the model catalog. Do not send project content for these checks. Never log Authorization headers or full key metadata. A valid key does not prove credit balance, endpoint eligibility, model access or a successful generation. Distinguish invalid key, insufficient credit, rate limit, offline/timeout and service errors. Retry only bounded non-inference checks; no paid retry loop.
5. Display/filter model choices by the task's required text/image/tool/structured-output capabilities. Configure Economy/Balanced/Quality plus tier mappings and supported effort/budget controls. Label catalog prices as timestamped estimates if displayed; no guaranteed savings or invented free usage.
6. Offer a small disclosed live test with bounded output/runtime. On acceptance, make a minimal request and normalize usage/resolved model. Do not treat key validation or catalog visibility as a live-generation test. Do not silently switch models/services when the selected route fails.
7. Save nonsecret configuration such as provider `openrouter`, approved API base URL, model routes and credential source/reference. Never save the key. Enter New/Resume only with configured connection/model routing; actual task execution must revalidate its required capabilities.

Proposed API checks use [current key](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-api-key) and [model catalog](https://openrouter.ai/docs/api/api-reference/models/list-all-models-and-their-properties). API requests use credentials in headers, not URLs. Implementation must prevent credential forwarding to unapproved hosts/redirects.

The OpenRouter adapter needs an API client plus a bounded agent/tool execution loop. Start with supplied-context analysis/report workers; expose local read tools only through an explicit controlled tool dispatcher. Tool-requiring tasks must use a supporting model and tested executor. Local/external writes and Figma integration still require their own implemented authorization and connector capability. A chat completion alone is not the complete orchestration implementation. [Official tool-calling guide](https://openrouter.ai/docs/guides/features/tool-calling).

## Errors, return paths and persistence

| Condition | Planned response |
| --- | --- |
| No CLI installed | OpenRouter setup remains selectable; otherwise show installation guidance/Retry/Exit. No Manual mode. |
| Native login canceled or failed | Preserve project and previous valid configuration. Offer Retry/another provider/Exit. |
| Environment variable missing | Offer hidden key input or return to provider selection. Never print a secret-setting command containing a supplied key. |
| Invalid/revoked key or insufficient funds | Explain the category without echoing key/provider response secrets. Offer credentials/account correction, another provider or Exit. |
| Network/service failure | Readiness unknown, not automatically invalid credentials. Bounded non-inference retry. |
| Unsupported model/effort/vision/tools | Require a compatible selection or block that task. No claimed full support. |
| User cancels setup | Discard pending secrets/settings; retain prior saved settings and all feature records. |
| Saved provider unavailable next time | Re-authenticate/reconfigure or explicitly choose another provider before workflow execution. |

New/Resume is a feature choice, not permission for a smoke test or automatic provider transfer. Save settings atomically only after a coherent configuration exists; retain verification timestamps and distinguish configured/auth-checked/live-verified. Never clear a working configuration because a new setup attempt was canceled. Secret redaction applies to error paths, subprocess arguments/environment diagnostics, test fixtures and run artifacts.

## Implementation order and acceptance

1. Refactor the existing Codex-only runtime into a common adapter contract without regression.
2. Implement provider-first init with the three branches and no Manual option; separate CLI detection, credential presence, native auth readiness and actual task capability states.
3. Complete Claude Code report-worker parity and verified model setup/native authentication handoff.
4. Implement OpenRouter hidden/environment credential handling, connection checks, model configuration and bounded report-worker API execution. Add the controlled tool loop before advertising tool-dependent orchestration.
5. Add model/usage normalization, interruption/recovery and stage-aware role scheduling while preserving workflow gates and writer ownership.
6. Run synthetic/contract tests for all branches, plus explicitly requested small live acceptance tasks for each account/provider. No automatic billable tests during setup or CI.

Acceptance must cover neither/one/both installed CLIs, OpenRouter-only users, canceled login/key entry, no TTY, key redaction on all failures, unavailable secure storage, expired credentials, no network, no credits, restricted models, failed live probes, retained settings after cancellation, explicit provider switching, and normal feature resumption without lost approvals. No provider may require another provider's CLI or credentials. User project data/settings/secrets stay outside the public tool repository.

## Current implementation boundary

Provider-first init, native CLI authentication handoff, hidden/environment OpenRouter setup, local profiles and explicit bounded report workers are implemented. Claude image transport, persistent OS credential-store integration, automatic stage-aware multi-role scheduling and write-enabled Figma agents remain unimplemented. Read the [implementation/test report](provider-implementation-report.md) before claiming live account verification or full workflow automation.
