# ADR-0001: Architecture and stack for <project name>

- **Status:** accepted
- **Date:** 2026-08-17
- **Deciders:** <name>
- **Skill version:** ai-app-blueprints v2.0.0 (research 2026-08)

## Context

An own project meant to become a product with a web UI. One tenant at first (ourselves), later probably several customers with their own data. The agents are to be embedded as a backend service behind an API, with access to documents (RAG) and relational data; models do not run locally. No cloud mandate; EU data residency desired, GDPR is a bonus, not a must. Team: Python-strong, development primarily with Claude Code.

## Options

1. **Blueprint A — Python backend as an API + Next.js frontend**: FastAPI + PydanticAI, Postgres/pgvector, Langfuse, LiteLLM, Docker; models via API in an EU region. Pros: fits the team, no lock-in, scaffolds very well with Claude Code. Con: two languages (a thin TS frontend).
2. **Blueprint B — TypeScript full-stack** (Next.js + Vercel AI SDK/Mastra): one language, fastest UI. Con: the backend team is Python; ML-heavy work is thinner.
3. **Blueprint C/D — managed platform** (AgentCore/Foundry): enterprise governance, but lock-in and overhead an own project does not need right now.

## Decision

We choose **blueprint A**: FastAPI + PydanticAI (LangGraph only for agents with a real state machine), PostgreSQL 17 + pgvector with Row-Level Security, Langfuse (self-hosted) for tracing, LiteLLM as the model gateway, Docker Compose on an EU server. Frontend: Next.js with the Vercel AI SDK against the FastAPI stream (PydanticAI's Vercel adapter). Multi-tenant from day one (`tenant_id` everywhere, RLS, context object, `tenant_settings`), but only one tenant created.

## Consequences

- Positive: portable; individual components (model, gateway, observability) replaceable one by one; the second tenant is an insert; a later move to AgentCore/Foundry stays possible because the agent logic remains framework-based and the tools exist as MCP servers.
- Negative: two languages; operations (compose, backups, updates) are on us; model tokens are the largest cost block.
- Harder later: switching to DB-per-tenant (only feasible through the repository layer — which is why it is mandatory).

## Revisit when …

- a customer demands physical data separation or their own cloud account (BYOK) → ADR-0002 (tenant isolation), ADR-0003 (model access)
- enterprise requirements arrive (identity, session isolation, many long-running agents) → evaluate blueprint C/D
- the streaming UI becomes the actual product and the backend stays thin → evaluate blueprint B
- the research is older than six months → re-check framework and pricing status
