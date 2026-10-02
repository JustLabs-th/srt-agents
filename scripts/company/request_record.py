"""Build/validate the company.request.v1 record (docs/02_REQUEST_MODEL.md).

Validation helper only; storage is the native thread attachment API.
"""

from datetime import datetime, timezone
import uuid

ATTACHMENT_TYPE = "company.request.v1"
REQUEST_TYPES = ("NEW_PROJECT", "MODIFY_PROJECT")
CHANGE_TYPES = ("FEATURE", "MODIFY_FEATURE", "BUGFIX", "REFACTOR",
                "PERFORMANCE", "MIGRATION", "MAINTENANCE")
FIELDS = {"schema_version", "request_id", "requested_by_user_id", "request_type",
          "change_type", "project_id", "description", "created_at"}
MAX_IDENTITY_BYTES = 256
MAX_PAYLOAD_BYTES = 64 * 1024


def new_record(requested_by_user_id, request_type, description,
               project_id=None, change_type=None, request_id=None, created_at=None):
    record = {
        "schema_version": 1,
        "request_id": request_id or str(uuid.uuid4()),
        "requested_by_user_id": requested_by_user_id,
        "request_type": request_type,
        "project_id": project_id,
        "description": description,
        "created_at": created_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if change_type is not None:
        record["change_type"] = change_type
    validate(record)
    return record


def validate(record):
    """Raise ValueError if the record is not a valid company.request.v1 payload."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    unknown = set(record) - FIELDS
    if unknown:
        raise ValueError(f"unknown fields: {sorted(unknown)}")
    if record.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    for key in ("request_id", "requested_by_user_id", "description"):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} is required")
    if len(record["request_id"].encode()) > MAX_IDENTITY_BYTES:
        raise ValueError("request_id exceeds 256 bytes")
    request_type = record.get("request_type")
    if request_type not in REQUEST_TYPES:
        raise ValueError("request_type must be NEW_PROJECT or MODIFY_PROJECT")
    change_type = record.get("change_type")
    project_id = record.get("project_id")
    if request_type == "NEW_PROJECT":
        if change_type is not None:
            raise ValueError("change_type is only valid for MODIFY_PROJECT")
        if project_id is not None:
            raise ValueError("project_id must be null for NEW_PROJECT")
    else:
        if change_type not in CHANGE_TYPES:
            raise ValueError("change_type is required for MODIFY_PROJECT")
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError("project_id is required for MODIFY_PROJECT")
    try:
        datetime.fromisoformat(str(record.get("created_at")).replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("created_at must be RFC 3339") from None
    return record


def attachment_params(thread_id, record):
    """Params for thread/attachment/add."""
    validate(record)
    return {"threadId": thread_id, "attachmentType": ATTACHMENT_TYPE,
            "identityKey": record["request_id"], "payload": record}
