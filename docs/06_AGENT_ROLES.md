# 06 — Company Agent Roles

## Principle

Use Codex's native agent/sub-agent mechanisms. Do not create a separate multi-agent runtime.

## Initial Roles

### PROJECT_MANAGER

Primary/root role for request execution.

Responsibilities:

- understand request scope,
- inspect project context,
- decide whether planning/delegation is useful,
- coordinate sub-agents,
- apply Ask-Human policy,
- integrate results,
- produce final task status/report.

### PLANNER

Use for sufficiently complex work.

Responsibilities:

- decompose work,
- identify dependencies/risks,
- define executable steps,
- identify missing high-impact requirements.

### CODER

Responsibilities:

- inspect implementation context,
- implement changes,
- run relevant checks,
- fix failures within scope.

### TESTER

Responsibilities:

- validate requested behavior,
- execute project checks,
- add/adjust tests when appropriate,
- report reproducible failures.

### REVIEWER

Responsibilities:

- review implementation against request and repository rules,
- identify regressions/risk,
- verify important acceptance expectations.

## Dynamic Composition

Do not require all roles for every task.

Small task:

```text
PROJECT_MANAGER → CODER → validation
```

Large task:

```text
PROJECT_MANAGER
→ PLANNER
→ CODER(S)
→ TESTER
→ REVIEWER
```

Parallel agents are allowed only when their work can be isolated/integrated safely.
