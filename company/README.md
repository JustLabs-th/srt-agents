# Local llama.cpp baseline

Build the company fork's CLI using the pinned toolchain and the BuildTools/px setup in [the baseline report](../docs/PHASE_0_BASELINE.md). Copy `llama-cpp.config.toml.example` to `llama-cpp.config.toml` and set the worker's model ID. Supply `LLAMA_API_KEY` through the process environment or ignored `company/.env`; `env_key` must contain the variable name, never the key value.

Run from a Windows host terminal using a workspace whose DACL the CLI account can provision. A fixture created inside another Codex sandbox may be owned by that sandbox account and fail native writable-root ACL setup. Keep `windows.sandbox = "unelevated"` and `sandbox_mode = "workspace-write"` for the verified setup.

```powershell
python scripts/company/local_codex.py exec --json -C E:\Projects\srt-agents-phase0-host-owned 'Inspect this test repository without modifying files.'
```

The launcher uses an isolated Codex home under `codex-rs/target/phase0-local-home`. Internal inference bypasses px only for the configured worker host through process-local `NO_PROXY`; dependency builds still use px. Global login and model settings are not changed.

The company fork's opt-in `features.flat_multi_agent_tools = true` exposes native collaboration tools as flat functions for the current worker. The flag defaults to false in the source and affects collaboration schemas only. Keep `features.multi_agent_v2.enabled = false` for this worker: V2 requires `agent_message` input items that it rejects with HTTP 400; the local baseline uses native V1 and standard messages. Handlers, permissions and the agent lifecycle remain native. This option requires rebuilding the fork; see D012 in [the decisions](../docs/13_DECISIONS.md).

Native app-server verification uses synthetic fixture inputs rather than real user/admin decisions:

```powershell
python scripts/company/phase0_app_server_check.py human --cwd E:\Projects\srt-agents-phase0-host-owned
python scripts/company/phase0_app_server_check.py approval --cwd E:\Projects\srt-agents-phase0-host-owned
python scripts/company/phase0_app_server_check.py approval-accept --cwd E:\Projects\srt-agents-phase0-host-owned
python scripts/company/phase0_app_server_check.py subagent --cwd E:\Projects\srt-agents-phase0-host-owned
python scripts/company/phase0_namespace_probe.py
```

The checker fails if required native events or results are absent. Approval accept permits only the exact marker command in the expected workspace and PowerShell wrapper; other approval requests are declined. The `git` scenario additionally permits three fixed commands to create a fixture branch, stage `calculator.py` and commit it. Run it only with a fresh disposable fixture containing the expected uncommitted calculator fix, an empty index and no existing `phase0/local-fix` branch. It uses a synthetic author and never pushes. It is intentionally not repeatable on an already committed fixture.

These scripts verify the existing runtime. They do not implement company identity, request ownership, USER/ADMIN routing or audit authorization.
