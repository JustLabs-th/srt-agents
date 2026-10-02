# 07 — Audit and Traceability

## Goal

Every meaningful request and decision must be attributable from human request to final code result.

## Trace Chain

```text
Company User
   ↓
Request
   ↓
Codex Session/Thread
   ↓
Agent / Sub-agents
   ↓
Tools / Commands / Decisions
   ↓
Human Inputs / Admin Actions
   ↓
Git Commit / PR / Result
```

## Actor Types

Support at least:

```text
USER
ADMIN
AGENT
SUBAGENT
SYSTEM
```

## Conceptual Audit Event

```text
event_id
request_id
session_id
actor_type
actor_id
action
timestamp
payload
```

## Required Attribution

The audit model must distinguish:

- original requester,
- person answering a product question,
- admin making a decision,
- admin performing an action,
- agent/sub-agent executing work.

Never overwrite `requested_by_user_id` when another person later participates.

## Required Queries

The system should eventually answer:

- Who requested this change?
- What was the request text/type?
- Which session/thread executed it?
- Which human decisions were requested and answered?
- Who approved or resolved admin gates?
- Which agents/sub-agents participated?
- What repository/branch/commit/PR contains the result?
- When did key events occur?

## Data Volume Principle

Do not retain disposable workspaces forever solely for audit.

Prefer durable metadata/events, relevant logs, diff/result references, and git commit/PR identifiers.
