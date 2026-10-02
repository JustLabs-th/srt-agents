# 02 — Request Model

## Top-Level Types

Only two top-level request types are defined:

```text
NEW_PROJECT
MODIFY_PROJECT
```

### NEW_PROJECT

Use when there is no existing primary codebase for the requested system/component.

Typical flow:

```text
Request
→ requirements discovery
→ architecture/project decisions
→ repository/project creation
→ implementation
→ test/review
→ result
```

### MODIFY_PROJECT

Use when an existing project/repository is the execution target.

Recommended subtypes:

```text
FEATURE
MODIFY_FEATURE
BUGFIX
REFACTOR
PERFORMANCE
MIGRATION
MAINTENANCE
```

Subtypes are descriptive and should not become separate top-level request lifecycles unless a future requirement proves the need.

## Minimum Request Data

```text
request_id
requested_by_user_id
request_type
project_id
change_type          # optional, mainly MODIFY_PROJECT
description
status
created_at
```

## Ownership

`requested_by_user_id` remains the original requester for the life of the request.

If another person later answers a requirement question or approves an action, record that actor separately rather than replacing request ownership.

## Request to Codex Session

Default conceptual mapping:

```text
1 Request/Task → 1 primary Codex session/thread
```

The same session should resume after user/admin input when the work is still the same request.
