# 11 — Local LLM Plan

## Status

The user requested local LLM execution during Phase 0. Use the existing llama.cpp server on `worker@192.168.100.26` through Codex provider configuration. Broader production-model evaluation remains a later phase.

## Reason

Keep deterministic mock-provider tests for:

- request semantics,
- autonomy behavior,
- ask-human routing,
- identity/audit,
- company policies.

This separates agent-system bugs from model-quality/provider-compatibility problems while local inference is brought into the baseline.

## Current Connection

- `http://192.168.100.26:8080/health` returns HTTP 200 with status `ok`.
- Authenticated `/v1/models` returns HTTP 200 and confirms model ID `qwen3.8-27b`.
- Authenticated `/v1/responses` returns HTTP 200, status `completed`, and `LOCAL_OK` for a minimal check.
- Source-built Codex receives streamed responses and function calls from this model. Native Windows sandbox shell reads work; the full coding fixture is still blocked on sandbox write access.
- SSH on port 22 timed out; no changes were made to the worker.
- This Codex source supports `wire_api = "responses"`; `wire_api = "chat"` is rejected.
- Credentials are loaded from `LLAMA_API_KEY` or ignored `company/.env`; the provider configuration contains only the environment-variable name.

See `../company/llama-cpp.config.toml.example` for the provider template. The local `company/llama-cpp.config.toml` selects the verified model. Run `python scripts/company/local_codex.py` with normal Codex CLI arguments to activate this configuration in an isolated runtime home under `codex-rs/target/phase0-local-home`; the default ChatGPT configuration is preserved.

## Current Runtime Limitations

- This custom model is absent from the bundled Codex metadata catalog, so Codex reports fallback model metadata.
- The initial Windows configuration had no sandbox backend selected; workspace-write downgraded to read-only. The local configuration now explicitly selects `windows.sandbox = "unelevated"`.
- With that backend, shell inspection succeeds but both `apply_patch` and shell file writes receive access-denied errors in the disposable fixture. The specific sandbox/ACL cause is not yet established; do not label the coding baseline passed.
- Resuming the first failed local thread exhausted API retries. A fresh recovery thread worked for reads; durable local-provider resume still needs investigation.

## Target

Use Codex provider/configuration mechanisms where possible so that the company distribution is not tied to one model.

Potential target architecture:

```text
Company Codex
    ↓
Model Provider / Compatible Endpoint
    ↓
Local Inference Runtime
    ├─ Qwen-family model
    ├─ DeepSeek-family model
    └─ other approved coding models
```

Potential serving technologies may include vLLM, SGLang, or another approved OpenAI-compatible runtime.

## Acceptance Criteria

Before switching production coding workloads to a local model, evaluate at least:

- tool-call reliability,
- instruction following,
- coding quality,
- long-context behavior,
- session stability,
- ask-human behavior,
- test-fix loop success,
- latency/throughput,
- resource usage.
