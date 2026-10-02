# 08 — Company Policy and Governance

## Purpose

Company policy constrains what autonomous Codex agents are allowed to do.

## Policy Areas

### Application Authorization

Manage user roles, project access, and action permissions inside Company Codex. The configured authentication method establishes identity; internal authorization determines which operations that identity may perform. AD integration is optional and does not change this boundary.

External groups may influence permissions only through explicit mappings controlled inside the software.

### Git

Example defaults:

- do not directly push protected branches,
- do not force-push protected/shared branches,
- use task/feature branches when policy requires,
- merge only when authorized.

### Environment

Example model:

```text
Development → highly autonomous
Staging     → policy-controlled
Production  → explicit admin authorization where required
```

### Security

Policy may restrict:

- secrets access,
- protected network access,
- privileged commands,
- destructive commands,
- production credentials,
- data exfiltration paths.

### Resources

Policy may govern:

- model/provider availability,
- budget/token limits,
- execution timeout,
- compute/storage quotas.

## Enforcement Strategy

Prefer native Codex extension/enforcement surfaces before core patches:

```text
Config → Instructions → Skills → Hooks → MCP/Tools → Core
```

## Principle

Policy should prevent unauthorized actions without forcing humans to approve routine low-risk development operations.
