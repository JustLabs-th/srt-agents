# 03 — AD Authentication and Internal Authorization

## Decision

Support optional Active Directory (AD) or company authentication/SSO integration, enabled through configuration, to authenticate users and supply their external identity.

Without AD, use a configured alternative authentication method, such as local authentication. AD is not a prerequisite for P0; both modes must retain stable local user references, internal authorization, and audit attribution.

Company Codex controls authorization inside the software: application roles, project access, and action permissions are managed internally.

The Company Codex distribution does not own employee passwords when an existing company identity provider is available.

## Local User Record

Maintain a local/shadow identity for stable references and authorization.

Suggested conceptual fields:

```text
id                    # internal stable user ID
external_subject      # immutable provider subject; nullable for local authentication
employee_id           # optional company identifier
username              # optional display/login alias
display_name
email
status
created_at
last_login_at
```

Prefer `external_subject` over email as the external identity key.

## Responsibilities

### AD / Company Auth

Owns:

- authentication,
- password/MFA policy,
- account lifecycle,
- authoritative company identity.

### Company Codex

Owns:

- internal user mapping,
- internally managed application roles and permissions,
- project/application authorization,
- request ownership,
- ask-human routing,
- audit attribution.

## Provisioning

For external authentication, prefer Just-In-Time provisioning. Local authentication uses a stable local user record without requiring AD.

```text
AD / Company login
→ validate identity/token
→ read external subject
→ find local user
→ create/update local mapping
→ load Company Codex roles/permissions
```

Provisioning an identity does not automatically grant elevated application permissions. AD group membership grants application roles only through an explicit mapping configured and governed inside Company Codex.

## Initial Application Roles

Suggested starting roles:

```text
USER
ADMIN
PROJECT_ADMIN
AUDITOR
```

These roles are managed inside Company Codex. External identity groups may be inputs to an explicit internal mapping; they are not the application's permission authority.
