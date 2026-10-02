# 13 — Architecture Decisions

## D001 — Codex Is the Harness

**Status:** Accepted

The project forks/extends Codex rather than creating a separate general-purpose harness around Codex.

## D002 — Two Top-Level Request Types

**Status:** Accepted

Top-level request types are:

```text
NEW_PROJECT
MODIFY_PROJECT
```

Modify subtypes remain secondary metadata.

## D003 — Autonomous by Default

**Status:** Accepted

The agent discovers available information and makes safe/reversible implementation choices without human interruption.

## D004 — Separate User and Admin Human Gates

**Status:** Accepted

Product/business decisions route to users.

Permission/security/infrastructure/credential/governance issues route to admins.

Semantic categories:

```text
USER_DECISION_REQUIRED
ADMIN_DECISION_REQUIRED
ADMIN_ACTION_REQUIRED
```

## D005 — Optional AD Authentication with Internal Authorization

**Status:** Accepted

The project supports optional AD/company authentication, enabled through configuration, and keeps a local/shadow user mapping for stable attribution. Without AD, a configured alternative such as local authentication may be used. Application roles, project access, and action permissions are controlled inside Company Codex in either mode.

AD availability is not a prerequisite for P0; AD integration may follow verification of internal identity and authorization.

AD group membership affects application permissions only through an explicit mapping configured and governed inside the software. Company password/account management remains with the authentication provider.

## D006 — Request Ownership Is Immutable Attribution

**Status:** Accepted

The original requester remains attached to the request. Later responders/approvers are captured separately.

## D007 — One Primary Session Per Request/Task by Default

**Status:** Accepted

Human-question pauses resume the same session/thread unless recovery requires otherwise.

## D008 — No Duplicate Git Engine

**Status:** Accepted

Codex uses git directly. Company work focuses on Gitea-specific API features and governance.

## D009 — Repository-Native Knowledge First

**Status:** Accepted

Use repository docs/instructions/skills before introducing vector RAG infrastructure.

## D010 — Local LLM Baseline in Phase 0

**Status:** Accepted

At the user's request, Phase 0 uses the existing company llama.cpp server through native Codex provider configuration. Verify Responses API and tool-call compatibility rather than assuming an OpenAI-compatible Chat Completions endpoint is sufficient.

Use deterministic mock-provider tests to separate harness behavior from model/provider issues. Broader production-model evaluation remains a later phase. This replaces the earlier decision to defer all local-model support.

## D011 — Upstream-Friendly Customization

**Status:** Accepted

Prefer config/instructions/skills/hooks/MCP/tools before modifying Codex core.

## D012 — Flat Native Collaboration Tools for Local Providers

**Status:** Accepted; native V1 local runtime and registration regressions verified.

The Phase 0 llama.cpp endpoint calls a flat function schema successfully but returns no function call for the same tool wrapped in a Responses namespace, even with `tool_choice = "required"`. A live sub-agent check fails because collaboration tools are not usable through this endpoint's namespace representation.

Existing V2 tool registration already supports plain function names when provider namespaces are unavailable, but the generic Responses provider advertises namespace support and offers no configuration switch to select that path. V1 tools always use a namespace. A skill, instruction, hook or MCP adapter cannot change these native schemas safely without duplicating the agent execution mechanism.

Add the opt-in feature `flat_multi_agent_tools` (default false). When enabled, V2 definitions use the existing flat registration path; V1 definitions expose each existing single-function namespace as a plain function with a matching registered name. Required child-management names use the same selection. Native handlers, parent/child lifecycle, encryption annotations and permissions remain enforced. Other tool namespaces and providers' default behavior retain their existing selection logic. This is a collaboration compatibility option, not a general namespace adapter.

The first flat V2 live test progressed to child creation, then both threads failed with HTTP 400 `Cannot determine type of 'item'`. Persisted history contains `agent_message`; a direct standard-message request passes while the corresponding agent-message request returns 400. Therefore keep `multi_agent_v2.enabled = false` for this worker and verify native V1, which uses standard messages. V2 end-to-end remains unsupported on the current worker; do not silently convert or discard its message envelopes.

The patch touches `features/src/lib.rs`, `core/src/tools/spec_plan.rs`, `core/src/tools/multi_agent_tool.rs`, registration regression tests and the generated config schema. Verify plain visible schemas and registered names together, retain the existing namespaced-path regressions, and exercise a real local-model V1 parent/child round trip. Enable the flat flag only in the company local configuration.

Upstream conflict risk is limited to feature registration and tool-plan construction. Disable the flag to recover existing behavior; remove the patch when upstream provides equivalent provider configuration or the local endpoint supports native namespace tools. Model fallback metadata and broader model evaluation are separate concerns.

## D013 — Request Record Stored as a Native Thread Attachment

**Status:** Accepted (design); native round trip pending runtime verification.

Phase 0B stores the immutable request record (`company.request.v1`, keyed by `request_id`) as a native thread attachment on the request's primary thread, instead of adding a request table, service or core field. Upstream's attachment API is persisted, idempotent per identity, supports reverse lookup and is copied on fork, which covers request ownership (D006) and request-to-session linkage (D007). No core change.

Consequences: mutable `status` is not stored in the record (attachments cannot be updated); durable transitions go to audit events (0E). The attachment API has no per-user authorization, so protecting the record from `remove`/forgery is a Phase 0C requirement. See `02_REQUEST_MODEL.md`.
