# 00 — Overview

## Product

**Company Codex Harness** is a company-specific distribution/fork of OpenAI Codex CLI.

The key architectural decision is:

> Codex is the harness. We extend Codex; we do not place another general-purpose harness around it.

## Objective

Create an autonomous software-engineering agent for internal company use that can receive software requests, work independently, use Codex agent/sub-agent/tool/session capabilities, and involve humans only when a genuine human decision or administrative action is required.

## Core Principles

1. **Autonomous by default** — discover before asking.
2. **Human decisions are exceptions** — not the normal execution path.
3. **User and Admin questions are different** — product decisions route to users; platform/governance issues route to admins.
4. **Optional AD/company authentication with internal authorization** — AD is enabled through configuration; an alternative authentication method can be used without AD. This software controls roles, project access, and action permissions in either mode.
5. **Trace everything** — request → session → agents → tools → human decisions → git result.
6. **Do not duplicate Codex** — use existing Codex capabilities before implementing new infrastructure.
7. **Minimize fork divergence** — config/skills/hooks/MCP before core patches.

## P0 Scope

P0 adds five capabilities:

1. Request model
2. Company identity mapping
3. Ask-Human routing policy
4. Autonomous execution policy
5. Audit attribution and traceability

Phase 0 baseline execution uses the company's existing llama.cpp inference server through a Codex provider configuration. Responses API and tool-call compatibility must be verified; deterministic mock tests provide a separate harness baseline.

## Later Phases

- company agent roles and policies,
- Gitea-specific extension surface,
- project/company knowledge integration,
- broader local LLM evaluation and production readiness,
- UI/admin experience,
- evaluation and operational metrics.

## Non-Goals for P0

- new agent loop,
- new session manager,
- new multi-agent framework,
- new shell/file-edit framework,
- new git engine,
- new sandbox engine,
- vector database by default,
- generic workflow platform,
- enterprise web portal before the core behavior is proven.
