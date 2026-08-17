---
name: ai-app-blueprints
description: Architecture and stack decisions for apps with AI agents (LLM apps, agent backends, RAG, MCP, multi-tenant SaaS), based on research from 2026-08. Runs a short interview, picks the right blueprint (lean Python stack, TypeScript full-stack, AWS Bedrock/AgentCore, Azure AI Foundry, self-hosted/GDPR), generates ADRs and a CLAUDE.md, and optionally scaffolds from a starter repo. Use whenever a new project with AI/LLM/agents is started, or when someone asks about tech stacks, architecture, framework choice (PydanticAI, LangGraph, Vercel AI SDK, Mastra, Bedrock, Azure Foundry, Vertex, Claude Agent SDK), embedding agents via API, agent data access, multi-tenancy, tenant isolation/RLS, GDPR/EU hosting, or a mobile app (Android/iOS, Expo/React Native, PWA) as a client of an agent backend — even if the request is just "start a new project", "how do I begin", or "which stack should we use". Not for plain data-analysis scripts, single prompts, or projects without an LLM component.
metadata:
  version: "2.0.0"
  research_date: "2026-08"
  template_repo: "https://github.com/JulesCyb/ai-app-starter"
  language: "en"
---

# AI App Blueprints

Make the same, evidence-backed decisions at every AI-agent project start instead of researching from scratch. The output is a set of ADRs, a `CLAUDE.md`, and optionally a project scaffold from the starter repo. Artifacts are written in the user's language; file names stay English.

## Flow

### 1. Establish context — one question block, not a back-and-forth

First read the existing repo (`pyproject.toml`, `package.json`, `docker-compose*.yml`, `README*`, `docs/adr/`) and ask nothing that is already answered there. Then put all open points into **one** block (`AskUserQuestion` if available):

1. **Context** — own project/internal tool, or client project (enterprise, compliance, multiple teams)?
2. **Tenants** — one (for now), several later, or several from day one?
3. **Interface** — none (API/CLI), web app with chat/streaming, an existing UI to integrate, or additionally a mobile app (Android/iOS — now or later)?
4. **Cloud mandate** — none, AWS, Azure, GCP, or EU provider/self-hosted required?
5. **Data protection** — standard (EU region + DPA), strict (EU providers or self-hosted only), or uncritical?
6. **Data sources** — relational data, documents (RAG), third-party systems (which)?
7. **Team and language** — Python, TypeScript, mixed?

If an answer is missing, assume a default and **say so**: own project, one tenant (but built multi-tenant), web app, no cloud mandate, EU region, documents + DB, Python.

### 2. Pick the blueprint

**The default is A** (Python backend as an API, optional Next.js frontend) — portable, the easiest to scaffold with Claude Code, no lock-in; write the agent logic so it can later move to C/D/E. Deviate from A only when an interview answer forces it:

- Team is TypeScript **and** the product is essentially a chat/React UI, no heavy RAG/eval pipelines → **B**
- Client on AWS → **C** · Client on Azure/M365 → **D** · Client on GCP → Vertex/ADK (analogous to C/D)
- Strict data protection or self-hosting required → **E**

If no trigger applies (including when unsure): **A**. A mobile app does not change the blueprint: it is just another client of the same API (section "Mobile clients" in `references/agent-architecture.md`).

Components, costs, lock-in, switching criteria: `references/blueprints.md`.

### 3. Check freshness — mandatory

The research dates from 2026-08 (`metadata.research_date`). If the project starts more than about six months later, tell the user and check current docs before pinning frameworks and versions (Context7 or the projects' `llms.txt`, `uv add`/`npm view` for versions). Never pin versions from the reference files blindly. Principles in this skill age slowly; product names and prices age fast.

Example of why this matters: between the research and the build of the starter repo, the MCP Python SDK moved from `FastMCP` to `MCPServer` (version 2.0).

### 4. Generate the artifacts

Always:
- `docs/adr/0001-architecture.md` from `assets/adr-template.md` (filled-in example: `assets/adr-0001-example.md`). Further ADRs only when something was actually decided: `0002-tenancy.md`, `0003-model-access.md`, `0004-hosting.md`, `0005-mobile.md` (template `assets/adr-0005-mobile.md`).
- `CLAUDE.md` from `assets/CLAUDE.md.template` — fill in the placeholders, delete what is unused, leave nothing generic.

Optional:
- Project scaffold: the starter repo (`metadata.template_repo`) applies to **blueprint A** — start from it (`git clone` and remove `.git`, or `degit`), replace names, ports, and placeholders; for E it works as a base (model serving is added on top). For B–D, create a minimal structure per the blueprint instead — dedicated starters are extracted from real projects, not invented up front.
- Frontend only for blueprint A with a UI, or B; approach in `references/agent-architecture.md` (streaming/UI section) and `docs/frontend.md` in the starter repo.
- Mobile app: only when question 3 names one; then fill in `assets/adr-0005-mobile.md` and put the backend duties from the "Mobile clients" section (real auth, API contracts, jobs, uploads, push) into the handover as tasks.

No code without an ADR: document the decision first, then build.

### 5. Handover

Summarize: chosen blueprint, the five most important decisions, open points, what had to be checked for freshness. Ask whether any findings should flow back into the skill (see Maintenance).

## Principles — apply in every project, regardless of blueprint

1. Agent logic runs as its own backend service with an API; never merge UI and agent. Models via API (Claude/GPT/Bedrock/Azure), not locally — except blueprint E.
2. A context object (`tenant_id`, `user_id`, roles) is passed through every request, agent run, tool call, and background job. Nothing reads global state.
3. Every table has a `tenant_id`, Postgres Row-Level Security is on, embeddings are data. The app's DB role is **not a superuser** — otherwise RLS does not apply.
4. Agents access data only through tools that run with the logged-in user's permissions. Never hand DB credentials to the model. Tools return only what is needed — everything returned ends up in the prompt at the model provider.
5. Build your own integrations as MCP servers — once, then use them in Claude Code, in the product, and on managed platforms.
6. Provider abstraction for models (framework provider or LiteLLM). Model choice, prompts, limits, and third-party credentials configurable per tenant, not in `.env`.
7. Observability from day one (Langfuse or OTel-compatible) with a tenant tag; costs attributable per tenant.
8. No low-code at the core. No secrets in the repo. EU region as the default, check the DPA.
9. Cache keys (embeddings, responses, prompt cache) include the `tenant_id`.
10. Start simple: a PydanticAI agent with tools. LangGraph only once an agent needs a real state machine with checkpoints or human-in-the-loop. Roughly 40% of "agent" tasks are a single model call with structured output.

## References — read only when needed

- `references/blueprints.md` — blueprints A–E, comparison table, switching criteria. Read in step 2.
- `references/agent-architecture.md` — backend as an API, own vs. managed agent runtime, data access via tools/MCP, streaming to the UI, state/checkpoints, observability, hosting, mobile clients. Read when building backend, UI, tools, or an app.
- `references/multi-tenancy.md` — one vs. many tenants, RLS patterns (SQL), context object (Python), decision table. Read as soon as question 2 is answered.
- `references/stack-2026-08.md` — condensed research: platforms (Bedrock/AgentCore, Azure Foundry, Vertex, OpenAI/Anthropic SDKs), frameworks, standards (MCP/A2A), self-hosting, GDPR/EU providers, what is obsolete. Read for concrete framework or platform questions.
- `references/research-2026-08.md` — full research report with sources. Only for detail questions.
- `assets/CLAUDE.md.template`, `assets/adr-template.md`, `assets/adr-0001-example.md`, `assets/adr-0005-mobile.md` — templates for step 4.

## Maintenance

Write new findings (a better library, a failed decision, a price or product change) into the matching reference file, bump `metadata.version` and `metadata.research_date`, add a changelog entry in `README.md`. After larger changes, rerun the test prompts in `evals/evals.json` (Claude Code: skill-creator plugin) and verify the skill still triggers on "new AI project" and does not trigger on "analyze this CSV".
