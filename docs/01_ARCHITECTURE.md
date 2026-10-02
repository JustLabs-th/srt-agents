# 01 — Architecture

## Baseline

```text
Company Codex Fork
       │
       ├─ Request semantics
       ├─ Identity / audit attribution
       ├─ Ask-Human routing
       ├─ Company policies
       ├─ Agent roles
       ├─ Skills / Hooks / MCP
       └─ Company-specific extensions
              │
              ▼
          Codex Core
              │
      ┌───────┼────────┐
      │       │        │
   Agents   Tools    Sessions
      │       │        │
      └───────┼────────┘
              ▼
        Model Provider
```

## Extension Strategy

Prefer, in order:

1. Config
2. Repository instructions / `AGENTS.md`
3. Skills
4. Hooks / policy enforcement
5. MCP / plugin / custom tools
6. Agent role configuration
7. Core modification

## Why

Every unnecessary core patch increases future upstream synchronization cost.

## Responsibility Boundaries

### Codex

Use upstream functionality for:

- agent execution loop,
- tools and shell execution,
- file inspection/editing,
- session/thread behavior,
- sub-agents,
- git command execution,
- sandbox/permission mechanisms,
- MCP/tool surfaces,
- model/provider behavior where supported.

### Company Extensions

Add only company-specific behavior:

- request semantics,
- company identity attribution,
- ask-human routing semantics,
- company governance policies,
- audit requirements,
- company/Gitea-specific tools,
- company knowledge access,
- approved local-model integration.

## Anti-Pattern

Do not build:

```text
Company Orchestrator
  → Company Session Manager
  → Company Agent Framework
  → Codex
```

unless a documented gap analysis proves that Codex cannot satisfy the requirement through its native extension surfaces.
