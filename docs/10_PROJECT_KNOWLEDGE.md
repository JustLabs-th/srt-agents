# 10 — Project and Company Knowledge

## Start With Repository-Native Context

Before introducing RAG infrastructure, use:

```text
AGENTS.md
REQUIREMENTS.md
ARCHITECTURE.md
DECISIONS.md
README / project docs
skills
.codex configuration
source code / tests / config
```

## Why

Most modification requests can be answered by inspecting the repository and its documentation.

Adding a vector database too early increases operational complexity without proving value.

## When to Add RAG / Knowledge MCP

Add a company knowledge service when relevant context lives outside the repository or is too large/distributed for repository-native discovery.

Examples:

- company engineering standards shared across many repositories,
- internal API catalogs,
- product/business documentation stored elsewhere,
- architecture knowledge spanning many systems,
- historical decisions not available in the target repository.

Recommended shape:

```text
Codex
  ↓
Company Knowledge MCP
  ↓
Search / RAG / Documents / Databases
```

Keep retrieval auditable and project/permission aware.
