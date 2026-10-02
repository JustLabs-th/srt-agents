# 14 — Upstream Sync Strategy

## Goal

Keep the company fork close enough to upstream Codex that security fixes, improvements, and new capabilities can be adopted without excessive merge cost.

## Rules

1. Do not modify upstream core when an extension point is sufficient.
2. Keep company-specific modules/configuration isolated where practical.
3. Avoid broad unrelated refactors of upstream code.
4. Add tests around every company behavior that touches core.
5. Record every intentional divergence in `13_DECISIONS.md` or a dedicated ADR.
6. Re-run P0 acceptance scenarios after each upstream merge/rebase.

## Suggested Git Model

Conceptually:

```text
upstream/openai-codex
        ↓ sync
company/main
        ↓
company feature branches
```

Choose merge or rebase strategy according to team policy, but make upstream provenance explicit.

## Required Upstream Regression Scenarios

After an upstream update verify:

- basic coding task,
- session/thread resume,
- Ask-Human routing,
- sub-agent execution used by company roles,
- sandbox/permission behavior,
- git/Gitea flow,
- audit attribution,
- configured provider behavior.

## Core Patch Checklist

Before accepting a core patch, document:

```text
Problem
Why config/skill/hook/MCP was insufficient
Files/components changed
Tests added
Expected upstream-conflict risk
Rollback/removal path
```
