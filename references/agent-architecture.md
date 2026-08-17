# Agent architecture: backend as an API, data access, streaming, state

## The three layers

```
Web UI (Next.js/React, streaming chat)
        │  HTTP/SSE
Agent backend (your API: FastAPI + PydanticAI/LangGraph)
   ├── Model API (Claude, GPT, Bedrock, Azure — via provider abstraction/LiteLLM)
   ├── Data (Postgres + pgvector, object storage) — only through tools with user permissions
   └── Tools/MCP servers (own systems, third-party APIs)
Langfuse/OTel records every run.
```

The UI is dumb: it sends messages and renders the stream. The intelligence lives in the backend. Models are replaceable external services.

## "Agents via API" — two variants, both valid

**Variant 1 — own backend service (default).** Agent logic runs in FastAPI (Docker, EU server or container service). The backend exposes endpoints like `POST /agents/assistant/run` and itself only calls the model API. Lean, portable, cheap. For long runs: a job queue (e.g. Postgres-based or Redis/RQ), a status endpoint, results in the DB.

**Variant 2 — managed platform.** The agent runs on Bedrock AgentCore, Azure Foundry Agent Service, or Vertex Agent Engine; the app talks to their API. Worth it with many long-running agents, enterprise identity, session isolation, auditing, or when the client mandates the platform. The same PydanticAI/Strands/LangGraph logic moves there.

Rule: write the logic so it does not stick to the hosting — framework agent + tools + context object, no platform-specific calls in the agent core.

## Agent data access

- The agent never gets raw DB credentials. It gets **tools**: "search the user's documents", "fetch revenue for month X", "create a case".
- Every tool is a backend function running with the logged-in user's permissions: `tenant_id`/`user_id` come from the context object, RLS filters in the DB, the tool checks roles.
- Documents via RAG from pgvector (filtered on `tenant_id`), structured data via SQL in the repository, third-party systems via MCP servers.
- Everything a tool returns ends up in the prompt and thus at the model provider → return only what is needed, choose an EU region and DPA, use zero-data-retention options where available.
- Budget for prompt injection through data: tool results are data, not instructions; writing tools need confirmation (human-in-the-loop) or tight guardrails.

## MCP servers as the integration layer

One MCP server per data source/third-party system, using the same tool functions as the backend (shared module, two entry points). Payoff: Claude Code during development, the product (PydanticAI can mount MCP servers as a toolset), Claude Desktop, later AgentCore/Foundry — without rewriting. In production the MCP server runs with auth (OAuth/token) and tenant context; locally via stdio for development.

Freshness caveat: MCP Python SDK 2.0 uses `from mcp.server.mcpserver import MCPServer` (formerly `FastMCP`). Check the current SDK docs before building.

## Streaming to the UI

- The backend streams via Server-Sent Events. With PydanticAI: `agent.run_stream(...)` and `stream_text(delta=True)` for plain text; for a Vercel-AI-SDK-compatible chat UI use `VercelAIAdapter.dispatch_request(request, agent=..., deps=..., sdk_version=6)` — then `useChat` hooks in the Next.js frontend work directly against the FastAPI backend. Alternatively the AG-UI adapter for generic agent UIs.
- Scaffold the frontend at project time with `npx create-next-app@latest` and `npm i ai @ai-sdk/react` (check current versions); the chat component points at the backend's `/api/chat` (proxy or direct URL, mind CORS).
- Show tool calls in the stream (the adapter emits tool events) so users can see what the agent is doing.

## State, memory, state machines

- Short-term: per-conversation message history in Postgres (`conversations`, `messages` with `tenant_id`).
- Long-term: only if needed — summaries/facts per user, clearly separated, deletable (GDPR).
- State machine (defined steps, resumption, approvals): LangGraph with the Postgres checkpointer. First check whether a PydanticAI agent with tools is enough.
- Human-in-the-loop: the workflow pauses at a node, waits for approval (UI action → endpoint), then continues; only clean with persisted state.

## Observability

- Langfuse (self-hosted or cloud) via OpenTelemetry: PydanticAI instrumentation on, `tenant_id`/`user_id` as trace attributes, cost per trace. Alternatives: LangSmith, Arize Phoenix, Logfire.
- From day one — not retrofitted. Without traces you debug agents blind.
- Audit log once there are multiple tenants: who ran which agent with which data and when.

## Hosting standard for blueprint A

- Docker Compose: `api`, `postgres` (pgvector image), optionally `litellm`, `langfuse` (use Langfuse's official compose file — version 3 needs ClickHouse/Redis/MinIO), optionally `minio`.
- Two DB roles: a migration role (owner) and an app role (no superuser, `NOBYPASSRLS`). The superuser from the Postgres image bypasses RLS — the app must never connect as it.
- Secrets via `.env` (not in the repo) or a secret manager; per tenant, encrypted in the DB.
- EU location; for clients with strict mandates see blueprint E.

## Mobile clients (Android/iOS)

An app does not change the blueprint: it is another client of the same API. Agent logic, tools, RLS, and model access stay untouched — the effort is in the backend, not the app.

**Three paths, check in this order**
1. **PWA / packaged web app** (installable Next.js UI, Capacitor or Trusted Web Activity for the Play Store): the cheapest test, enough for internal tools. Limits: no native feel, restricted camera, push, background.
2. **Expo / React Native** — the default once a Next.js frontend exists or is planned: same language and types, the Vercel AI SDK also runs in React Native (streaming against `/api/chat`), monorepo with a shared package (types, hooks, API client generated from FastAPI's OpenAPI schema). Components are not shared 1:1 (HTML vs. native views), logic is. The most comfortable path for Claude Code.
3. **Native (Kotlin + Jetpack Compose, or Swift/SwiftUI)** — only with a reason: deep OS integration (camera workflows, offline, background services), a native team, or the app *is* the product. Flutter and Kotlin Multiplatform are middle roads, rarely a win without a TS team.

**Backend duties once an app arrives**
- **Real auth**: dev headers are untenable on a device. OIDC with PKCE via an identity provider (Keycloak/Zitadel self-hosted, or Auth0/Firebase Auth), short-lived access tokens + refresh tokens stored securely (Keystore/Keychain), implement `AUTH_MODE=jwt` in the backend.
- **Freeze API contracts**: app versions live for months. `/v1/` prefix, no breaking changes, the OpenAPI schema as the contract, a generated client, a deprecation window.
- **Long runs as jobs**: no phone holds minute-long connections cleanly. Start job → status endpoint or push → result in the DB. SSE streaming only for chat.
- **File uploads** (photos of documents): signed upload URLs to object storage, server-side processing, tenant prefix.
- **Push notifications** (FCM/APNs): device tokens per user with `tenant_id`, unregister on logout.
- **Hardening**: per-user rate limits, Play Integrity / App Attest only when needed, certificate pinning only if the client demands it.
- **Data protection**: no content in push payloads, server-side token revocation, logs without user data.

**Not needed**: AI on the device. Models stay behind the API; on-device models (Gemini Nano & co.) are at most a later addition for small offline tasks.

**Order**: web → PWA as a test → Expo when it gets serious → native only with a reason. Record the decision as an ADR (`assets/adr-0005-mobile.md`).
