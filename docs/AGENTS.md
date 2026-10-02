# AGENTS.md — Company Codex Harness

## 1. Mission

This repository is a company-specific distribution/fork of OpenAI Codex CLI.

The goal is **not** to build another harness around Codex. Codex itself is the agent harness and execution runtime. We extend it only where company requirements are not already satisfied by upstream Codex.

Primary goals:

1. Autonomous software delivery by default.
2. Human involvement only when a real product/business decision, platform/admin decision, or required admin action is needed.
3. Full traceability from company user → request → Codex session/thread → sub-agents → tools/actions → git result.
4. AD/company authentication integration with authorization controlled inside this software.
5. Preserve upstream compatibility and make future upstream merges practical.

Read all relevant files in `docs/` before changing architecture or behavior.

---

## 2. Architectural Rule: Codex Is the Harness

Do **not** introduce another orchestration/harness layer that duplicates Codex capabilities.

Before implementing a new subsystem, verify whether upstream Codex already provides the capability through:

1. configuration,
2. `AGENTS.md`,
3. skills,
4. hooks/policies,
5. MCP/plugins/tools,
6. existing agent/sub-agent capabilities,
7. app-server/protocol surfaces,
8. core changes only as a last resort.

Preferred customization order:

```text
Config
  ↓
AGENTS.md / instructions
  ↓
Skills
  ↓
Hooks / policies
  ↓
MCP / plugins / tools
  ↓
Agent role configuration
  ↓
Codex core modification
```

If a requirement can be satisfied without modifying Codex core, do not modify core.

---

## 3. P0 Scope

P0 consists of five company capabilities:

1. Request model
2. Company identity mapping
3. Ask-Human routing policy
4. Autonomous execution policy
5. Audit attribution / traceability

Do not expand P0 with a new web platform, vector database, workflow engine, queue, custom agent loop, custom sandbox engine, or generic framework unless explicitly approved.

---

## 4. Request Types

Top-level request types are intentionally limited to:

```text
NEW_PROJECT
MODIFY_PROJECT
```

`MODIFY_PROJECT` may have subtypes such as:

```text
FEATURE
MODIFY_FEATURE
BUGFIX
REFACTOR
PERFORMANCE
MIGRATION
MAINTENANCE
```

Do not add new top-level request types without a documented decision.

Every request must be attributable to a company user.

Minimum conceptual fields:

```text
request_id
requested_by_user_id
request_type
project_id (nullable for NEW_PROJECT until created)
description
status
created_at
```

See `docs/02_REQUEST_MODEL.md`.

---

## 5. Identity and Authentication

Support optional Active Directory (AD) or company authentication/SSO integration, enabled through configuration. When enabled, the external provider supplies identity; Company Codex controls application authorization internally. Without AD, use a configured alternative authentication method, such as local authentication.

AD availability is not a prerequisite for P0. Preserve stable local identity, internal authorization, and audit attribution regardless of the authentication method.

Manage application roles, project access, and action permissions inside this software. AD group membership does not automatically grant application permissions; any group-to-role mapping must be explicitly configured and governed inside the software.

This project must **not** become a second password/account system if company authentication already exists.

Maintain a local/shadow user record only for:

- stable internal identity,
- authorization mapping,
- request ownership,
- audit references,
- project roles,
- human-decision routing.

Conceptual mapping:

```text
AD / Company Auth / SSO
        ↓
 external subject
        ↓
 Local User Record
        ↓
 Internal Roles / Permissions
        ↓
 Request / Session / Audit
```

Prefer immutable provider subject identifiers over email as the external identity key.

See `docs/03_IDENTITY_AUTH.md`.

---

## 6. Ask-Human Policy

The agent must not ask a human for information it can reasonably discover from:

- repository contents,
- documentation,
- configuration,
- tests,
- existing code conventions,
- available tools,
- non-destructive inspection commands.

The agent should make safe, low-risk, reversible implementation decisions itself.

Human interaction is reserved for unresolved decisions that materially matter.

### 6.1 Route to USER

Ask the requesting/product user when the missing answer changes **what the product should do**.

Examples:

- missing business rule,
- product behavior ambiguity,
- UX/workflow choice,
- domain rule,
- acceptance-criteria ambiguity,
- conflicting product requirements.

Canonical semantic event:

```text
USER_DECISION_REQUIRED
```

### 6.2 Route to ADMIN

Ask an administrator when the issue concerns **what the agent is allowed or able to do**.

Examples:

- repository permission,
- credentials/secrets,
- sandbox restriction,
- network restriction,
- security policy,
- privileged execution,
- deployment permission,
- infrastructure/resource policy,
- organization-level model/budget policy.

Use two semantic event classes:

```text
ADMIN_DECISION_REQUIRED
ADMIN_ACTION_REQUIRED
```

`ADMIN_DECISION_REQUIRED` requires a policy/authorization decision.

`ADMIN_ACTION_REQUIRED` means the environment is missing something actionable, such as an expired credential.

See `docs/04_ASK_HUMAN_POLICY.md`.

---

## 7. Autonomous Execution Policy

Default behavior is autonomous.

Decision order:

```text
1. Can the agent discover the answer itself?
   → Yes: discover it and continue.

2. Can the agent make a safe, reversible, low-risk implementation choice?
   → Yes: decide and continue; record assumptions when useful.

3. Does the unresolved answer change product/business behavior?
   → Ask USER.

4. Does it concern permission/security/infrastructure/credentials/governance?
   → Ask ADMIN.

5. If still unclassified:
   → prefer a safe pause over silently making a high-impact assumption.
```

Do not ask users questions such as:

- where a source file is,
- what test runner the repository uses,
- what naming convention exists,
- which dependency version is installed,
- whether an existing architecture uses a service/repository pattern,
- what database schema currently exists.

Inspect first.

See `docs/05_AUTONOMY_POLICY.md`.

---

## 8. Session / Thread Semantics

Default conceptual rule:

```text
1 Request/Task → 1 primary Codex session/thread
```

Do not create a new session merely because the current session is waiting for user/admin input.

Resume the same session for:

- user answers,
- admin decisions/actions once resolved,
- normal retry after test/validation feedback when context remains valid.

Project knowledge must not depend solely on long-lived session memory.

---

## 9. Agent Roles

Use Codex's existing agent/sub-agent mechanisms rather than creating a separate multi-agent framework.

Initial company roles:

```text
PROJECT_MANAGER
PLANNER
CODER
TESTER
REVIEWER
```

Roles are capabilities, not mandatory workflow stages.

Small tasks may use only:

```text
PROJECT_MANAGER → CODER → validation
```

Larger tasks may use:

```text
PROJECT_MANAGER
      ↓
   PLANNER
      ↓
 CODER(S)
      ↓
   TESTER
      ↓
  REVIEWER
```

Do not spawn agents merely to satisfy a fixed diagram.

See `docs/06_AGENT_ROLES.md`.

---

## 10. Git and Gitea

Codex already has shell/git capability. Do not build a duplicate Git engine.

Company-specific Gitea integration should only cover Gitea-specific operations that are not naturally handled by git itself, for example:

- issue retrieval,
- pull-request creation,
- PR comments,
- reviewer assignment,
- repository metadata,
- merge operation when allowed by policy.

Prefer a small MCP/plugin/skill/tool surface over a large Gitea orchestration subsystem.

Git governance belongs to company policy, e.g.:

- no direct push to protected branches,
- no force-push unless explicitly allowed,
- merge/deployment permissions governed by policy.

See `docs/09_GITEA_EXTENSION.md`.

---

## 11. Audit and Traceability

Every meaningful action must be attributable.

The system must be able to answer:

- Who requested the work?
- What was requested?
- Which session/thread executed it?
- Which agent/sub-agent acted?
- Which human answered a question?
- Which admin approved or resolved an action?
- What files/tools/commands materially changed the result?
- Which commit/PR corresponds to the result?

Actor types should support at least:

```text
USER
ADMIN
AGENT
SUBAGENT
SYSTEM
```

Do not overwrite request ownership when another user later responds or approves. Record separate actor attribution.

See `docs/07_AUDIT_TRACEABILITY.md`.

---

## 12. Project Knowledge

Start simple.

Use repository-native knowledge first:

- `AGENTS.md`,
- project docs,
- architecture docs,
- requirement docs,
- decision records,
- skills,
- config.

Do not add a vector database in P0 merely because the project is AI-related.

Add Company Knowledge MCP/RAG only when repository-native context is demonstrably insufficient.

See `docs/10_PROJECT_KNOWLEDGE.md`.

---

## 13. Local LLM

Phase 0 baseline execution uses the company's local llama.cpp server, as requested. Integrate it through existing Codex provider/configuration surfaces and verify Responses API and tool-call compatibility before treating it as a usable coding provider.

Keep deterministic mock-provider tests as a separate baseline so that harness/policy failures can be distinguished from local-model quality failures. Broader model evaluation remains a later phase.

Target architecture may include an OpenAI-compatible inference endpoint backed by vLLM/SGLang or another approved runtime.

Do not hard-code the company distribution to one model.

See `docs/11_LOCAL_LLM.md`.

---

## 14. Upstream Compatibility

This is a fork, so maintainability matters.

For every modification to upstream core:

1. document why an extension surface was insufficient,
2. isolate company-specific code where practical,
3. add tests,
4. avoid unnecessary formatting/refactoring of unrelated upstream code,
5. record the decision in `docs/13_DECISIONS.md`,
6. consider the future cost of upstream rebasing/merging.

See `docs/12_IMPLEMENTATION_PLAN.md` and `docs/14_UPSTREAM_SYNC.md`.

---

## 15. Engineering Rules

Before implementation:

1. inspect existing upstream behavior,
2. locate the smallest extension point,
3. write/update acceptance criteria,
4. make the smallest coherent change,
5. run relevant tests,
6. document behavioral changes.

Do not silently introduce infrastructure or architectural layers not required by the current phase.

If a requirement is unclear and is not covered by the Ask-Human policy, document the ambiguity instead of inventing a permanent architectural decision.

---

## 16. P0 Definition of Done

P0 is complete when the fork can demonstrate all of the following in a real repository:

1. A company user submits either `NEW_PROJECT` or `MODIFY_PROJECT`.
2. The request is linked to a stable local user identity from the configured authentication method, with AD integration optional.
3. Codex performs discoverable/reversible decisions autonomously without unnecessary questions.
4. A product/business ambiguity is surfaced as `USER_DECISION_REQUIRED`.
5. An infrastructure/permission/credential issue is surfaced as `ADMIN_DECISION_REQUIRED` or `ADMIN_ACTION_REQUIRED`.
6. The same Codex session/thread resumes after the human response.
7. Audit records identify requester, responders/approvers, session/thread, agent activity, and final git result.
8. No duplicate agent loop, session framework, git engine, or sandbox framework has been introduced outside Codex without an approved decision.
