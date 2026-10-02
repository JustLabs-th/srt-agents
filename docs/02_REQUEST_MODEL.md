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

---

## Phase 0B — Concrete Record and Linkage

Status: **defined; storage mechanism chosen (native thread attachment, no core change); runtime verification pending** (see Verification).

### Storage: native thread attachment

Upstream already provides a persisted, typed, per-thread JSON store (`thread/attachment/add|list|remove`, reverse lookup `thread/attachmentOwner/list`; `state/src/runtime/thread_attachments.rs`). The request record is stored as one attachment on the request's primary thread:

```text
attachment_type = "company.request.v1"
identity_key    = <request_id>
payload         = immutable request record (below), <= 64 KiB
```

Properties relied on (verified by source inspection):

- `add` is idempotent per `(thread, type, identity_key)`; a repeated add returns `Existing` with the **original** payload, so a second writer cannot overwrite the requester (D006).
- `attachmentOwner/list(type, identity_key)` resolves `request_id → thread` (and the reverse via `list`), satisfying request-to-session linkage (D007) without a new table.
- Attachments are copied to forks (`copy_thread_attachments`), so a fork keeps request linkage.

### Immutable record

Schema: [`company/request-record.schema.json`](../company/request-record.schema.json).

```text
schema_version        1
request_id            opaque, unique, <= 256 bytes (identity_key)
requested_by_user_id  internal stable user id (docs/03), never an email/AD name
request_type         NEW_PROJECT | MODIFY_PROJECT
change_type           required for MODIFY_PROJECT, absent for NEW_PROJECT
project_id            string for MODIFY_PROJECT; null for NEW_PROJECT
description           non-empty text
created_at            RFC 3339 UTC
```

`status` is deliberately **not** in the record: attachments cannot be updated, only removed and re-added, and a remove/re-add would break the immutability guarantee above.

### Decisions and open items

- **Status** is not stored in Phase 0B. Lifecycle (thread active/idle/waiting-for-input) is derivable from the thread; durable status transitions are recorded as audit events in Phase 0E. If that proves insufficient, document the gap before adding storage.
- **NEW_PROJECT `project_id`** is null in the immutable record. The project created later is recorded as an audit event (0E), not a mutation.
- **Authorization gap (for 0C):** the app-server attachment API has no per-user authorization; any connected client can call `remove`. Requester immutability is only guaranteed against `add`. Protecting `company.request.*` attachments from removal/forgery must be enforced by the company entry point/authorization layer in 0C, or by a core guard if no extension surface suffices (which would require a decision entry per `14_UPSTREAM_SYNC.md`).
- One request maps to one primary thread; creating a second thread with the same `request_id` is not prevented by storage (uniqueness is per thread). The entry point must check `attachmentOwner/list` first.

### Acceptance criteria

1. A valid `NEW_PROJECT` and a valid `MODIFY_PROJECT` (with subtype) record are accepted; invalid ones (unknown type, missing `change_type` on MODIFY, `change_type` on NEW, empty description, non-null `project_id` on NEW, missing requester) are rejected before any write.
2. Attaching a record to a thread returns `created`; re-attaching a record with a different requester returns `existing` and the stored `requested_by_user_id` is unchanged.
3. `attachmentOwner/list` for the `request_id` returns exactly the owning thread.
4. The record survives an app-server restart.
5. No change to upstream core crates.

### Verification

- Unit tests (model-free, any OS): `cd scripts/company && python -m unittest test_request_record`.
- Native round trip (model-free, needs the built binary and a disposable fixture): `python scripts/company/phase0_app_server_check.py request --cwd <fixture>`. Covers criteria 2–4.
