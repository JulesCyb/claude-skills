# Blueprints A–E (as of 2026-08)

Five stack compositions the research identified as viable. The blueprint fixes hosting, language, and platform — the principles from `SKILL.md` apply in all five.

## Blueprint A — Lean Python stack (default for own projects and internal tools)

**Components**
- Backend/API: FastAPI (async), package manager `uv`
- Agent logic: PydanticAI (type-safe agents, structured output, native MCP); LangGraph only for agents with a real state machine (checkpoints, human-in-the-loop, resumption)
- Data: PostgreSQL + pgvector (data, metadata, and embeddings in one DB), Row-Level Security on
- Models: via API — Claude/GPT/Gemini directly, via Bedrock/Azure in an EU region, or with LiteLLM as a gateway (virtual keys, budgets, fallbacks, provider switch via one config line). Ollama/vLLM only for development or blueprint E.
- Observability: Langfuse (self-hosted or cloud), OTel-based, with a tenant tag
- Integrations: own MCP servers for third-party systems
- Operations: Docker Compose on an EU server (Hetzner, IONOS, netcup …) or a container service; S3-compatible object storage (MinIO/Hetzner) for files
- Frontend (optional): Next.js/React with the Vercel AI SDK consuming the FastAPI stream; PydanticAI ships adapters for the Vercel AI SDK stream format and AG-UI

**Strengths:** fits a Python team, scaffolds extremely well with Claude Code (dense conventions, Pydantic typing), zero vendor lock-in, GDPR-capable, cheap (infra + tokens).
**Weaknesses:** no native frontend; a second language for the UI (thin TS frontend).
**Costs:** server + tokens; Langfuse and LiteLLM are free self-hosted.
**Lock-in:** minimal — every component individually replaceable.

## Blueprint B — TypeScript full-stack (when the product is a chat/React app)

**Components**
- Next.js + Vercel AI SDK (v6: streaming, tool-loop agents, structured output via Zod, MCP) — or Mastra when real workflows, cross-session memory, evals, or RAG are needed
- Postgres + pgvector, Langfuse
- Hosting: the Vercel platform *or* Cloudflare/Railway/Fly/self-hosted (Docker, Coolify) — the AI SDK is a library and does not require the Vercel platform

**When B instead of A:** frontend + agent should live in one repo and one language, the streaming UI is the center of the product, the team is TS-strong. As soon as ML-heavy work arrives (fine-tuning, complex retrieval pipelines, evals), add a Python backend (A+B combination: Python backend, TS frontend).
**Strengths:** one language across the stack, end-to-end type safety, very fast time-to-MVP.
**Weaknesses:** thinner ML ecosystem; LangGraph.js lags behind Python.
**Lock-in:** none for the AI SDK; the Vercel *platform* has framework-shaped lock-in (ISR, middleware, Fluid Compute) and bandwidth price jumps.

## Blueprint C — Enterprise on AWS

**Components**
- Amazon Bedrock AgentCore (GA since 2025-10-13): Runtime (up to 8 h, MicroVM session isolation), Gateway (tools/MCP), Memory, Identity, Observability, Browser, Code Interpreter, Policy/Evaluations
- Agent code: Strands Agents SDK (AWS, Python/TS) or LangGraph/PydanticAI — AgentCore is framework- and model-agnostic
- Models: Bedrock (Claude, Nova, OpenAI models, Llama, Mistral …), EU geo cross-region inference (Frankfurt/Ireland/Paris)
- Knowledge: Bedrock Knowledge Bases; Guardrails
- Standards: MCP and A2A native

**Pricing (order of magnitude, official AgentCore pricing page 2026):** Runtime/Browser/Code Interpreter ≈ $0.0895/vCPU-hour + $0.00945/GB-hour (active CPU only), Gateway $0.005/1000 calls, Memory $0.25/1000 events (long-term $0.75/1000 records/month). Model tokens always on top — the largest block.
**EU/GDPR:** AgentCore fully available in Frankfurt; DPA available; residual CLOUD Act risk as with all US hyperscalers.
**Lock-in:** medium to high (AgentCore services), mitigated by framework-/model-agnostic agent logic.
**When:** the client is on AWS and needs enterprise security, session isolation, long runs, auditing.

## Blueprint D — Enterprise on Azure (the most common case in German enterprises)

**Components**
- Azure AI Foundry Agent Service (built on the OpenAI Responses API, wire-compatible), private networking (BYO VNet), Entra RBAC, MCP over private paths, OTel tracing, evaluations
- Agent code: Microsoft Agent Framework 1.0 (GA 2026-04; merger of AutoGen and Semantic Kernel, Python + .NET, MCP + A2A native) or Responses-API-compatible agents (OpenAI Agents SDK)
- Models: Azure OpenAI, Claude in Foundry, DeepSeek, Llama, Phi, and more; search: Azure AI Search
- No markup on the agent layer: costs = model tokens + used tools (Bing, AI Search, Logic Apps)

**EU/GDPR:** EU regions, DPA, the most established enterprise platform in Germany.
**Lock-in:** high (Azure), migration eased by Responses API compatibility.
**When:** the client is on Azure/M365 — then D is almost always the pragmatic default.
**GCP analogue:** Vertex AI / Gemini Enterprise Agent Platform with ADK (code-first, Python/Go/Java/TS), Agent Engine as a managed runtime (≈ $0.0864/vCPU-h + $0.009/GB-h), Model Garden incl. Claude, A2A native.

## Blueprint E — Maximum data sovereignty / self-hosted

**Components**
- Model serving: vLLM (production, throughput, continuous batching) or SGLang; Ollama only for prototypes/homelab
- Models with tool calling: Qwen3 family (30B-A3B as the sweet spot on a 24 GB GPU), gpt-oss 20B/120B (Apache 2.0), Llama, Mistral; flagship sizes (235B+) need multi-GPU
- Agent logic: PydanticAI or LangGraph, pgvector, Langfuse self-hosted, LiteLLM self-hosted (data stays in-house)
- Everything in Docker/Kubernetes on owned or rented EU hardware; optionally EU providers (Mistral, IONOS AI Model Hub, STACKIT) for load peaks

**Hardware, roughly:** 16 GB VRAM → 8–12B model; 24 GB → 30B-A3B/32B (Q4); 80 GB (H100) → 70B FP8 / gpt-oss-120b.
**Strengths:** full data sovereignty, no DPA with US providers needed, no token costs.
**Weaknesses:** ops effort, hardware investment, models below frontier level; cost break-even vs. APIs only at very high volume.
**When:** public sector, healthcare, contracts with an EU-only clause, high predictable throughput.

## Comparison

| Criterion | A Python lean | B TS full-stack | C AWS AgentCore | D Azure Foundry | E self-hosted |
|---|---|---|---|---|---|
| Best for | own projects, internal tools, products with a Python backend | chat/React products | AWS enterprise | Azure/DE enterprise | max. GDPR |
| Claude Code fit | very high | high | medium | medium | high |
| Time-to-MVP | fast | very fast | medium | medium | slow |
| Lock-in | minimal | SDK none / platform medium | medium–high | high | none |
| GDPR/EU | good | good | good (EU geo) | good (EU + DPA) | maximum |
| Costs | tokens + infra | tokens + hosting | usage + tokens | tokens + tools | hardware + ops |
| Scaling/governance | build yourself | build yourself | enterprise-grade | enterprise-grade | build yourself |
| MCP/A2A | yes (framework) | yes (SDK/Mastra) | yes, native | yes, native | yes (framework) |

## Switching criteria

- **A → A + Next.js frontend:** as soon as a web UI with streaming is needed. The backend stays.
- **A → B:** only when the backend is deliberately meant to be TypeScript (TS team) and no ML-heavy work is planned.
- **A → C/D:** when enterprise requirements arrive (identity, session isolation, many long-running agents, auditing) or the client mandates the cloud. Agent logic in PydanticAI/Strands/LangGraph moves along; tools as MCP servers move along too.
- **A → E:** when data protection becomes strict, or volume is high enough that self-hosting pays off.
- **PydanticAI → LangGraph (individual agents):** when a flow needs defined steps, resumption after crash/waiting, an audit trail, or human approval.
- **pgvector → Qdrant/Weaviate:** only at very large data volumes or metadata-heavy filtering; the DB choice accounts for just 5–10% of RAG quality (chunking, embedding model, and retrieval pipeline matter more).
