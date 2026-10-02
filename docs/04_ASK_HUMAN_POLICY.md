# 04 — Ask-Human Policy

## Goal

Humans should be involved only when the agent cannot safely and correctly continue without a real human decision or administrative action.

## Routing Model

```text
Uncertainty
   ↓
Can repo/docs/tools answer it?
   ├─ Yes → Discover and continue
   └─ No
        ↓
Can agent make a safe, reversible, low-risk decision?
   ├─ Yes → Decide and continue
   └─ No
        ↓
Does it change product/business behavior?
   ├─ Yes → USER_DECISION_REQUIRED
   └─ No
        ↓
Does it concern permission/security/infra/credentials/governance?
   ├─ Decision needed → ADMIN_DECISION_REQUIRED
   └─ Missing admin action → ADMIN_ACTION_REQUIRED
```

## USER_DECISION_REQUIRED

Use when the missing answer determines **what the product should do**.

Examples:

- password-reset token expiration not defined,
- one or two approvers not defined,
- login on multiple devices not defined,
- delete immediately vs trash/retention not defined,
- UX/workflow choice changes business behavior,
- product requirements conflict.

The requester is the default routing target unless project ownership rules designate another product owner.

## ADMIN_DECISION_REQUIRED

Use when an administrator must make an authorization/governance decision.

Examples:

- allow production deployment,
- allow privileged execution,
- allow network access to a protected environment,
- authorize access to a repository/environment,
- increase a governed model/resource/budget limit.

## ADMIN_ACTION_REQUIRED

Use when a decision is not the problem; an administrator must perform an operational action.

Examples:

- refresh expired Gitea credentials,
- configure a missing secret,
- restore repository access,
- provision required infrastructure,
- enable an approved network route.

## Questions That Must Not Be Asked

Do not ask humans for facts the agent can inspect, such as:

- file locations,
- existing naming conventions,
- current framework/dependency versions,
- test commands discoverable from project config/CI/docs,
- current DB schema,
- existing project architecture,
- whether a pattern is already used in the codebase.

## Question Quality

When asking a human:

1. state what is missing,
2. explain why it blocks or materially affects the task,
3. provide concrete options when possible,
4. state consequences/tradeoffs briefly,
5. ask one decision-focused question rather than dumping internal reasoning.
