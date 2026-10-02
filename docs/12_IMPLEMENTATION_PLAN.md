# 12 — Implementation Plan

## Phase 0A — Upstream Baseline

Goal: prove the fork works before company changes.

Tasks:

1. Fork upstream Codex.
2. Build from source.
3. Run CLI against a test repository.
4. Verify session/thread start and resume behavior.
5. Verify sub-agent behavior available in the chosen upstream version.
6. Verify user-input / approval behavior relevant to this project.
7. Verify sandbox/tool execution behavior.
8. Verify git workflow in a disposable repository.
9. Document gaps rather than assuming missing capabilities.

Baseline real-model execution now targets the existing company llama.cpp server. Verify its authentication, Responses API, streaming, and tool-call compatibility through Codex provider configuration. Keep mock-provider tests to isolate harness behavior.

Deliverable: baseline verification report.

## Phase 0B — Company Request Semantics

Implement/define:

- `NEW_PROJECT`,
- `MODIFY_PROJECT`,
- request metadata,
- request ownership,
- request-to-session linkage.

## Phase 0C — Identity

Implement/define:

- authentication contract with optional AD/company integration,
- local user mapping,
- internally managed application roles, project access, and action permissions,
- stable audit identity.

P0 must be demonstrable without an AD connection, using a configured alternative authentication method. AD integration can be added after the internal identity/authorization behavior is proven.

## Phase 0D — Ask-Human + Autonomy

Implement semantic handling for:

```text
USER_DECISION_REQUIRED
ADMIN_DECISION_REQUIRED
ADMIN_ACTION_REQUIRED
```

Prove:

- discoverable questions are not asked,
- reversible implementation choices are made autonomously,
- product ambiguity routes to user,
- platform/governance blockers route to admin,
- the same session resumes after resolution.

## Phase 0E — Audit

Record enough metadata/events to trace:

```text
User → Request → Session → Agent/Subagent → Human Decisions → Git Result
```

## Phase 1 — Roles and Company Policy

- company agent roles,
- autonomy/security/git policies,
- policy enforcement through existing Codex extension points.

## Phase 2 — Gitea + Project Knowledge

- minimal Gitea-specific tool surface,
- repository-native documentation standard,
- add Knowledge MCP only if proven necessary.

## Phase 3 — Local LLM + Evaluation

- expanded local provider evaluation after the Phase 0 llama.cpp connection,
- coding/tool-use benchmarks,
- compare against baseline provider/model,
- operational metrics.

## Phase 4 — UI / Operations

Only after core behavior is stable:

- request UI,
- project view,
- pending user/admin decisions,
- audit/log view,
- agent/session visibility,
- operational administration.

## Engineering Rule

At every phase, ask:

> Does upstream Codex already provide this capability?

If yes, extend/configure it. Do not rebuild it.
