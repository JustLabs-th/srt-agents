# Phase 0A — Upstream Baseline Verification

Date: 2026-10-02

Status: **Phase 0A verified for the configured local native V1 path, including coding/test-fix, resume, user-input, approval, sandbox and Git workflow. V2 worker incompatibility is documented; company P0 implementation remains pending.**

## Baseline

- Repository: `JustLabs-th/codex`, local folder `E:\Projects\srt-agents`.
- Branch: `main`.
- Source commit: `8d44977aa2fb9ae1b128660668dc5b36966613fa`.
- Host: Windows, PowerShell.
- Company specification files are currently untracked; they are not part of the source commit above.
- A narrow opt-in native tool-schema compatibility patch is verified for the local provider; company request/identity/routing runtime is not yet implemented.

## Executed Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Required Rust toolchain | Ready | Installed the repository-pinned toolchain; `rustc +1.95.0 --version` reports `1.95.0 (59807616e 2026-04-14)` |
| Cargo | Ready | `cargo +1.95.0 --version` reports `1.95.0 (f2d3ce0bd 2026-03-21)` |
| MSVC tools | Compiler/linker setup corrected | BuildTools contains `libcmt.lib`; loading its Developer Shell resolves the initial linker failure |
| Pinned Git dependencies | Fetch succeeded with system Git | Retry downloaded crossterm, tungstenite, tokio-tungstenite and other Git dependencies |
| crates.io access | px endpoint probe passed | Explicit curl through `http://127.0.0.1:3128` returns `Proxy-Agent: Px` and HTTP 200 for the previously failing opentelemetry index URL |
| CLI build | Passed | Locked build completed in 5m 31s using px and BuildTools Developer Shell |
| CLI version/help | Passed | Built binary reports `codex-cli 0.0.0` and renders CLI/exec help; this is the source workspace version |
| Existing ChatGPT login status | Verified before switching provider | Elevated `login status` reports logged in; sandbox-only invocation cannot find the home directory |
| Blocking human-input round trip | Passed | 1 test passed, 0 failed/ignored |
| Nonblocking default-mode input | Passed | 1 test passed, 0 failed/ignored |
| Thread resume/history overrides | Passed | 1 test passed, 0 failed/ignored |
| Sub-agent instruction precedence | Passed | 12 parameterized cases passed, 0 failed/ignored |
| Real coding task | Passed with local provider | Recovery fixture changed only calculator.py; all 3 unittest cases pass and git diff contains the expected one-line fix |
| llama.cpp health | Passed | `http://192.168.100.26:8080/health` returns 200 with `ok` |
| llama.cpp authenticated model/Responses checks | Passed | Model list confirms `qwen3.8-27b`; `/v1/responses` returns 200 and `LOCAL_OK` |
| Local Responses streaming / tool calls | Passed | Source-built CLI receives streaming responses, issues tools, and reads fixture files |
| Local fixture file writes | Passed after correcting fixture ownership | Host-created fixture accepts writes under the same native unelevated Windows sandbox; outer-sandbox-owned fixture remains a retained failure case |
| Windows filesystem boundaries | Passed | Workspace write succeeds; sibling workspace and .git writes are denied; read-only profile denies file creation |
| Local-provider durable resume | Passed on successful coding thread | Restarted CLI resumes the same thread ID and recalls the bug, changed file, 3 passing tests and uncommitted result without tools |
| Local user-input round trip | Passed | Blocking native request receives synthetic Subtract answer; request resolves and next turn recalls it in the same thread |
| Local approval round trip | Passed, accept and decline | Synthetic decline prevents execution; exact allowlisted harmless command executes after synthetic accept |
| Local Git result | Passed in disposable fixture | Agent creates phase0/local-fix and commits only calculator.py as bbc83c6; no push |
| Local sub-agent | Passed with native V1 flat tools | Parent spawns a real child, waits for CHILD_BASELINE_OK and closes it; sender/receiver thread linkage verified |
| Native collaboration regression | Passed | 8 core tool-plan cases, including flat V1/V2 registration, unchanged namespace paths and V2 encryption markers; 1 schema fixture case passed |

Initial build command, from `codex-rs`:

```powershell
cargo build --locked -p codex-cli --bin codex
```

Cargo's built-in Git fetch failed with HTTP 407. The retry used the installed Git client, which successfully fetched the pinned Git dependencies:

```powershell
cargo build --locked -p codex-cli --bin codex --config net.git-fetch-with-cli=true
```

Both builds ran with approved elevated access for toolchain/cache writes and dependency downloads. The retry still failed at the crates.io index. This is not evidence of a source compilation error or a missing dependency revision.

## Proxy Follow-up

The user confirmed that the machine already uses px. Its process is running and the session's HTTP/HTTPS/ALL proxy variables point to `127.0.0.1:3128`. No global Cargo proxy override was found. An elevated curl probe through px successfully retrieved headers from the exact index URL that failed during the earlier builds.

The next build attempt explicitly routes Cargo through px, without changing global proxy settings or bypassing the company proxy:

```powershell
$env:CARGO_HTTP_PROXY = 'http://127.0.0.1:3128'
cargo build --locked -p codex-cli --bin codex --config net.git-fetch-with-cli=true
```

This attempt downloaded hundreds of crate archives through px. A follow-up disabled Cargo HTTP multiplexing after observing download timeouts. This is a conservative session setting; the successful archive downloads already began before that change, so it is not established as the cause of the 407 fix. The precise reason why the earlier Cargo attempt returned 407 has not yet been established. The earlier blanket classification as a missing admin proxy setup was premature.

Compilation then exposed a separate `LNK1104` failure for `libcmt.lib`. The selected Community linker had no matching library at its installation path, while BuildTools contains it. Loading BuildTools Developer Shell supplies the correct compiler/library environment and compilation proceeds.

Current command, from `codex-rs`:

```powershell
& 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\Launch-VsDevShell.ps1' -Arch amd64 -HostArch amd64 -SkipAutomaticLocation
$env:CARGO_HTTP_PROXY = 'http://127.0.0.1:3128'
$env:CARGO_HTTP_MULTIPLEXING = 'false'
cargo build --locked -p codex-cli --bin codex --config net.git-fetch-with-cli=true
```

Settings are scoped to the build process; no global Cargo/proxy configuration was changed.

Do not put proxy credentials or tokens in repository files, reports, or chat. Keep the pinned toolchain and lockfile intact while resolving access.

## Source Inspection Findings

These findings identify existing implementation surfaces; they are **not runtime pass results**.

| Concern | Existing surface | Remaining company behavior |
| --- | --- | --- |
| CLI dispatch | `codex-rs/cli/src/main.rs` | Company request entry/metadata |
| Thread lifecycle | `codex-rs/core/src/thread_manager.rs` | Immutable request ownership and request-to-thread linkage |
| Human questions / approvals | `core/src/tools/handlers/request_user_input.rs`, `core/src/session/handlers.rs`, `app-server/src/bespoke_event_handling.rs` | USER vs ADMIN routing and separately attributed responders |
| Extension registration | `app-server/src/extensions.rs`, `ext/extension-api/src/` | Evaluate isolated company extensions before core changes |
| Sub-agents | `core/src/agent/`, `core/src/tools/handlers/multi_agents_v2/` | Company roles and requester/actor propagation |
| History / storage | `rollout`, `state`, thread-attachment protocol | Durable request and audit metadata with authorization checks |
| Authentication | `app-server/src/external_auth.rs`, `agent-identity` | These inspected paths concern ChatGPT/agent identity; optional AD and internal user permissions need a separate integration contract |

## Verification After Dependencies Are Downloaded

The locked CLI build, version and help checks have completed. Run commands below inside BuildTools Developer Shell with px configured.

Then run existing focused integration tests, using their mock Responses service rather than requiring a real model credential for these tests:

```powershell
$env:RUST_MIN_STACK = '8388608'
$env:CARGO_HTTP_PROXY = 'http://127.0.0.1:3128'
cargo test --locked -p codex-app-server --test all request_user_input_round_trip --config net.git-fetch-with-cli=true
cargo test --locked -p codex-app-server --test all thread_resume_supports_history_and_overrides --config net.git-fetch-with-cli=true
cargo test --locked -p codex-app-server --test all request_user_input_default_mode_forwards_non_blocking --config net.git-fetch-with-cli=true
cargo test --locked -p codex-app-server --test all spawned_subagents_apply_configured_developer_instruction_precedence --config net.git-fetch-with-cli=true
```

The four app-server commands above executed 15 cases in total, all passing with no ignored cases. The first test build took 4m 50s; subsequent filtered tests reused the built runner.

Additional core tests were selected during source inspection but have not been run:

```powershell
cargo test --locked -p codex-core --test all cold_root_resume_restores_agent_identity_and_role_on_followup --config net.git-fetch-with-cli=true
cargo test --locked -p codex-core --test all approval_matrix_covers_group --config net.git-fetch-with-cli=true
```

These mock tests supplement, rather than replace, the following real CLI scenarios:

| Scenario | Pass criterion | Current status |
| --- | --- | --- |
| Coding / test-fix / git | In an isolated temporary repository, CLI edits a small program, passes its tests and produces the expected git diff | Passed with local inference in host-created fixture |
| Session resume | Reopen the same thread and retain the previous task context | Passed on coding thread |
| Sub-agent | Spawn and integrate a child agent's result with visible parent/child linkage | Passed with native V1 and opt-in flat tools |
| Human input | Ask a question, accept an answer and continue on the same thread | Passed with synthetic answer through native app-server |
| Approval / sandbox | Confirm a protected action is gated and allowed actions execute under the selected Windows sandbox | Filesystem boundaries and native accept/decline passed with synthetic fixture decisions |
| Git workflow | Use a disposable branch, inspect the diff and retain a local result commit | Passed; fixture branch phase0/local-fix, commit bbc83c6 |

The disposable fixture is `E:\Projects\srt-agents-phase0-t4_eq5eq`. It has a local initial commit and an intentional addition bug; the initial Python unittest run exits 1. No production repository code was used for the live coding smoke test.

The initial model from user config, `gpt-6.1-sol`, was rejected by the CLI's ChatGPT API with HTTP 400. An account catalog check listed other models, but the user then requested local inference. No successful cloud coding run is claimed and the default user model config was not changed.

Local inference now uses `company/llama-cpp.config.toml` with `qwen3.8-27b` and the wrapper `scripts/company/local_codex.py`. The wrapper loads credentials from the process environment or ignored `company/.env`, copies the credential-free config into an isolated Codex home, and routes this internal worker directly without changing global proxy or ChatGPT settings.

The user's initial local config placed the key value in `env_key`. That field expects a variable name. It now references `LLAMA_API_KEY`; the value was moved into ignored `company/.env` and was not printed or committed. Authenticated model listing and a minimal Responses request both passed.

Local thread `01a0fb8a-cbce-7ad0-88c1-482969984c90` received streamed tool calls but all shell commands were policy-blocked while the Windows sandbox backend was disabled. The local config now selects `windows.sandbox = "unelevated"`; this preserves native sandbox enforcement. A resume attempt on that thread exhausted response retries. Fresh recovery thread `01a0fb91-14ae-7271-8f23-3b545387881b` read the fixture and identified the bug, but both patch and shell writes were denied. Its persisted turn context confirms workspace-write policy. The ownership diagnosis and subsequent successful recovery are recorded below.

### Windows sandbox ownership diagnosis and recovery

A model-free repro failed in seconds on the original fixture:

```powershell
python scripts/company/local_codex.py sandbox -P :workspace -C E:\Projects\srt-agents-phase0-t4_eq5eq -- powershell.exe -NoProfile -Command "[System.IO.File]::WriteAllText('sandbox-probe.txt','sandbox-ok'); if (!(Test-Path sandbox-probe.txt)) { exit 1 }"
```

The result was access denied, exit 1. The original fixture owner is `SRT99PC301\CodexSandboxOffline`, while the host CLI runs as `SRT99PC301\admin`. Its ACL grants Authenticated Users Modify but contains no writable-root capability ACE. Modify does not include permission to change the DACL. In `windows-sandbox-rs/src/spawn_prep.rs`, the legacy backend discards errors from `ensure_allow_write_aces`, so this setup failure appears later as a tool write denial.

The recovery changes fixture ownership by creating a new workspace using the host account, rather than relaxing sandbox policy or broadening ACLs on existing projects. `E:\Projects\srt-agents-phase0-host-owned` is owned by the host account, contains copies of the same two fixture source files, and has initial local Git commit `de9631a`. The identical repro passes there under the same native restricted-token backend. The old fixture remains intact as evidence; arbitrary existing workspaces have not been repaired or verified.

Run these checks from the host terminal/account that owns the test workspace. Running the launcher inside another managed sandbox is not equivalent: it may lack a home directory or create workspaces owned by the outer sandbox account. A writable-root ACL must be provisionable by the CLI account. This is a workspace setup requirement, not a reason to select full access.

Filesystem checks using `sandbox -P :workspace` accepted file creation in the recovery workspace, denied creation in the original sibling workspace, and denied creation inside the recovery `.git`. A `sandbox -P :read-only` run using `Set-Content -ErrorAction Stop` denied creation in the recovery workspace. The first read-only probe used a .NET method and was stopped by PowerShell constrained language before testing file access; only the subsequent cmdlet probe counts as filesystem evidence. Network and interactive approval boundaries were not tested here.

Local recovery thread `01a0fb9f-e218-7780-9023-f16954f26f73` then completed the live coding scenario under `workspace-write` and `approval_policy=never`: it read the files, removed the extra `+ 1`, ran `python -m unittest -v` (3 passed), and displayed the expected one-line Git diff. The tests were unchanged and no result commit or push was made. This verifies shell-based edits; a successful `apply_patch` call was not separately exercised.

### Lifecycle and Git continuation

CLI durable resume of `01a0fb9f-e218-7780-9023-f16954f26f73` returned the previous off-by-one fix, `calculator.py`, 3 passed tests and no commit, without issuing tools. This is a successful process restart; the earlier unrelated retry failure remains historical evidence.

`scripts/company/phase0_app_server_check.py` is a verification client for native JSON-RPC, not a production company agent loop. It reuses the launcher's isolated configuration and credentials. Its synthetic answers/approvals are test inputs and must not be represented as real USER/ADMIN attribution or P0 routing.

| Scenario | Thread | Observed result |
| --- | --- | --- |
| Blocking input | 01a0fba7-58c7-7743-9a33-15aa119bdc91 | Native question calc_policy, synthetic Subtract response, serverRequest/resolved and completed turn; next turn remembers Subtract |
| Approval decline | 01a0fba7-a767-7dd2-b777-da1aa82546fa | Native command approval resolved with decline; command item status declined, no output/exit code; agent stops |
| Approval accept | 01a0fbad-f845-7b03-8dec-345dc8f844c1 | Exact allowlisted Write-Output command executes once after accept, marker output and exit 0 |
| Git workflow | 01a0fbae-dd18-76b0-b5d6-3a636ed37544 | Agent inspects diff, creates branch, stages calculator.py and commits after three exact allowlisted approvals |
| Initial sub-agent | 01a0fba7-c75e-7720-9450-3f6bf4007180 | No native spawn; the checker correctly fails on missing parent/child linkage |

The Git result is `bbc83c6e4a964a95d63da8fbb8731de694939e3c`, parent `de9631a255e3a761903c6ea222bd0f11fc84b088`, in the disposable host-owned fixture. The checker independently verifies branch, commit file list and absence of tracked uncommitted changes. Author identity is synthetic Baseline Verification, scoped to the test process. Only the exact three fixture Git commands are accepted; other approval requests are declined. The source fork has not been committed or pushed. Re-running the Git scenario requires a fresh fixture with the uncommitted calculator fix.

The initial Git diff command emitted a nonfatal PowerShell profile/constrained-language warning, then displayed the expected diff with exit 0. This warning does not change the result.

The direct diagnostic `scripts/company/phase0_namespace_probe.py` compares the same function as a flat schema and as a Responses namespace, using tool_choice required: the flat request returns baseline_ping, while the namespaced request completes without a function call. This supports a namespace compatibility gap in the current model/server path; it does not isolate whether the server or model is responsible. A standard message succeeds while an otherwise equivalent agent_message request returns HTTP 400.

### Verified local collaboration configuration

The opt-in `features.flat_multi_agent_tools = true` exposes native collaboration functions using plain schemas and matching registered tool names. The source default is false, so existing namespaces retain their normal behavior. For this worker keep `features.multi_agent_v2.enabled = false`: the attempted flat V2 parent `01a0fbbd-fa94-78c3-aabf-5450e92c6f87` created child `01a0fbbe-12f9-7480-8672-3278ed84fbc6`, but both failed with HTTP 400 Cannot determine type of item when the runtime used agent_message input. V2 live behavior is therefore not verified or supported on the current worker. D012 records the reason for the native compatibility patch and the V1 choice.

The final native V1 run passes: parent `01a0fbcb-68ef-7861-aaa1-05ad7e367b55` spawns child `01a0fbcb-8203-77e2-9f6b-b5462ff17420` with fork_context false and inherited local model. The child completes with exactly CHILD_BASELINE_OK; the parent's native wait returns the completed state, closeAgent completes, and the parent reports the result. The checker asserts the actual native spawn/linkage and completed child state, rather than accepting a claimed marker in a parent narrative.

Both flat registration tests were observed failing before their respective fixes. Final core regression runs pass 8 cases, including the default namespaced families, configurable V2 namespace, encryption markers on flat V2 messages and Bedrock behavior. The generated schema matches its fixture (1 passed). The locked CLI rebuild succeeds. No upstream orchestration, child lifecycle or sandbox engine was replaced.

After the final rebuild, native human-input check `01a0fbcd-ae3b-72f1-a241-c9c9c041ad36` passes on two turns; decline check `01a0fbcd-cb8d-7ea0-aa34-f26cd9117b41` and accept check `01a0fbcd-e1bb-7541-ae50-0c87ab9783c6` pass. Coding thread `01a0fb9f-e218-7780-9023-f16954f26f73` resumes again, runs all 3 fixture tests successfully and reads the actual bbc83c6 commit hash. Git diff against HEAD confirms the fix is committed and tests remain unchanged. The model's final narrative incorrectly called the fix uncommitted despite the hash; native tool output and independent Git checks are the authoritative result. Untracked __pycache__ and sandbox-probe.txt remain disposable test artifacts.

This completes the selected Phase 0A smoke scenarios with known compatibility limits. Synthetic replies/approvals do not prove company authentication, authorization, USER/ADMIN routing or audit attribution; those remain Phases 0B–0E. Network sandbox enforcement and production workspace ACL provisioning were not evaluated.

The custom model triggers fallback-metadata warnings because it is not present in Codex's model catalog. AD remains optional.

## Phase 0 Continuation

Proceed to 0B request semantics, then 0C internal identity/authorization with optional AD, 0D Ask-Human/autonomy, and 0E audit. Use the verified native V1/flat local configuration and preserve the mocked harness baseline. The existing lifecycle and attachment surfaces are candidates to evaluate, not an approved final storage design.
