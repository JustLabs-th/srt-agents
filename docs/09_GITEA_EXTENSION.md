# 09 — Gitea Extension

## Decision

Do not build a duplicate Git subsystem.

Codex can use normal git operations through its existing execution/tool capabilities.

## Company-Specific Surface

Add only operations that are Gitea/API-specific or materially easier/safer as explicit tools.

Candidate operations:

```text
get_issue
create_pull_request
get_pull_request
comment_pull_request
assign_reviewer
get_repository_metadata
merge_pull_request   # policy-gated
```

## Preferred Implementation

Use a small MCP/plugin/tool/skill integration.

## Governance

Credentials should be scoped according to company policy.

Codex should not receive broader Gitea permissions than required for the assigned task/project.

Protected-branch and merge rules remain company governance concerns.
