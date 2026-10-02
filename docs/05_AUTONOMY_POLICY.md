# 05 — Autonomous Execution Policy

## Default

The Company Codex agent is autonomous by default.

## Required Behavior

The agent should:

1. inspect before asking,
2. use repository context before external assumptions,
3. make reversible implementation choices itself,
4. run relevant tests/checks,
5. fix failures when the requested scope permits,
6. record material assumptions where useful,
7. stop only when a true decision/action gate is reached.

## Safe Agent Decisions

Typically agent-owned:

- locating files/modules,
- following repository naming patterns,
- choosing internal helper/function names,
- using the framework already adopted by the repo,
- choosing an implementation consistent with existing architecture,
- selecting/refining tests,
- fixing ordinary compile/lint/test failures,
- refactoring locally when necessary for the requested change and low risk.

## Human Gates

Do not autonomously invent:

- new business rules,
- product policy,
- irreversible data behavior,
- security exceptions,
- production permissions,
- organizational governance decisions.

## Reversible Assumptions

A reversible assumption may be taken when:

- impact is local,
- it follows existing code/repository convention,
- no business behavior is materially altered,
- it can be changed later without migration/data/security consequences.

## Failure Behavior

When blocked:

- classify the blocker using the Ask-Human policy,
- preserve the current session/thread,
- surface the minimal required question/action,
- resume after resolution.
