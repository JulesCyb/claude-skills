# Research report: best tech stacks for AI/agent apps 2026 (as of 2026-08)

Original question: which stacks for apps with AI are viable in 2026, specifically with meaningful agent integration — for own projects and consulting contexts, self-hosted and managed cloud (incl. AWS Bedrock), GDPR as a bonus, no low-code, developed primarily with AI coding agents in the CLI (Claude Code). Source list at the end of `stack-2026-08.md`.

## TL;DR
- For own projects, a lean Python stack is the right choice (FastAPI + PydanticAI or LangGraph + Postgres/pgvector + Langfuse + Docker, models via API gateway/LiteLLM or locally via Ollama/vLLM). Fits a Python base, scaffolds excellently with Claude Code, no vendor lock-in. TypeScript (Next.js + Vercel AI SDK or Mastra) only pays off when the product itself is a React/chat UI and frontend + agent should live in one language/repo.
- For German consulting/enterprise clients, the existing cloud decides, not the "best" framework: Azure AI Foundry Agent Service (dominant in Germany), AWS Bedrock AgentCore, or Google Vertex/Gemini Enterprise Agent Platform — all three GA 2025/2026, all with EU regions (Frankfurt), MCP and A2A support. GDPR-maximal is a self-hosted stack (vLLM + open models like Qwen3/gpt-oss) or an EU provider (Mistral, IONOS AI Model Hub, STACKIT).
- The standards layer is settled: MCP (Model Context Protocol) is the de-facto standard for tool integration (Linux Foundation governance; per the MCP blog of Dec 9, 2025, over 97M monthly SDK downloads and ~10,000 active servers), A2A for agent-to-agent communication. Build tools as MCP servers and they are framework- and vendor-portable. Do not build new work on: the OpenAI Assistants API (sunset August 26, 2026), plain LangChain "Classic" as an orchestrator, AutoGen/Semantic Kernel separately (merged into the Microsoft Agent Framework).

## Key findings
1. Language: Python remains the default for agent logic; TypeScript wins at the product/UI edge. The AI/ML library depth has a multi-year head start; for RAG pipelines, evals, and orchestration, Python gets there faster. TypeScript is superior when the product is a Next.js/React app with streaming chat. Both are the strongest ecosystems for AI coding agents because they dominate the training corpus.
2. Framework consolidation: in Python, LangGraph (stateful/graph-based, the production default) and PydanticAI (type-safe, lean, fast start) have emerged as the two load-bearing options; plus the provider-native SDKs (OpenAI Agents SDK, Claude Agent SDK, Google ADK, AWS Strands). In TypeScript, the Vercel AI SDK (v6) and Mastra are the pillars.
3. MCP + A2A are infrastructure standards, not hype. New MCP spec (2026-07-28) with a stateless core.
4. Managed platforms are paid by usage plus model tokens. AgentCore and Vertex Agent Engine have no base fee on orchestration; Azure Foundry Agent Service adds no markup on the agent layer. The largest cost block is always model tokens.
5. Self-hosting pays off for compliance and high, predictable throughput — rarely purely for cost. vLLM (and SGLang) are the production serving stack; Ollama is for prototypes/homelab. Tool-calling-capable open models in 2026: the Qwen3 family, gpt-oss (20B/120B), Llama, Mistral, DeepSeek.

## 1. The starting articles — context
The article by Diego Vogel (diego.works, May 2026) is a deliberately "pseudo-scientific" experiment: one prompt, 3 LLMs, 6 runs each. Leaderboard: Rails+Hotwire, Next.js+TypeScript, Phoenix+LiveView on top. Caveat: it covers web frameworks for agent-assisted web development, not AI/agent frameworks. Transferable findings: (a) convention density in the training corpus beats "explicit vs. implicit"; (b) static typing is a tiebreaker, not a gate; (c) every LLM has a bias (Claude→Phoenix, ChatGPT→Rails, Gemini→Next.js); (d) AGENTS.md/CLAUDE.md and pinned docs measurably raise the success rate.

The Hackmamba/dev.to article (May 2026) defines the AI stack layers (app/UI, backend, orchestration, retrieval/memory, model, data, eval/monitoring, deployment) and shows empirically that Python/JS/TS produce markedly more stable LLM-generated results than Flutter/Swift/Kotlin. Core rule: "put the AI logic where the model is strongest" — a Python/TS backend, whatever the UI.

## 2. Python vs. TypeScript
Python — strengths: the deepest AI ecosystem (PyTorch, Hugging Face, vLLM, LangGraph, PydanticAI, LlamaIndex, DSPy); research lands in Python first; the best choice for RAG, evals, model experiments, data pipelines; async is mature via asyncio/FastAPI; excellent for AI coding agents. Weaknesses: no native frontend; package management historically fragile — `uv` has largely solved that; runtime type errors without Pydantic/type hints.

TypeScript — strengths: one language across the whole stack; streaming chat UI, edge deployment, end-to-end type safety; the compiler catches breaking changes during SDK migrations; per GitHub Octoverse 2025 the most-used language on GitHub for the first time in August 2025. Weaknesses: ML-heavy work is thinner; LangGraph.js lags behind Python.

The typical combination: Python backend + TypeScript frontend. For internal tools without a demanding UI, Python alone suffices.

Vercel: the Vercel AI SDK (open-source TS library, v6 June 2026; unified provider API, streaming, structured output via Zod, tool calling, an `Agent` abstraction, durable workflow agents; runs anywhere) vs. the Vercel platform (paid hosting optimized for Next.js; lock-in via framework-bound features, bandwidth price jumps). Alternatives: Cloudflare, Netlify, Railway, Render, Fly.io, self-hosted via Docker/Coolify.

## 3. Managed cloud / enterprise platforms
AWS Bedrock AgentCore (GA October 13, 2025): Runtime (up to 8 h, MicroVM session isolation), Gateway, Memory, Browser, Code Interpreter, Identity, Observability, Policy, and Evaluations (preview since Dec 2025). Framework-agnostic (LangGraph, CrewAI, LlamaIndex, Strands, Google ADK, OpenAI Agents SDK); MCP and A2A support; any foundation model. Pricing: Runtime/Browser/Code Interpreter each $0.0895/vCPU-h and $0.00945/GB-h (active CPU only); Gateway $0.005/1000 API calls, semantic search $0.025/1000, tool indexing $0.02/100 tools/month; Memory $0.25/1000 events, long-term $0.75/1000 records/month. EU/GDPR: AgentCore fully in Frankfurt; EU geo cross-region inference keeps data in EU regions. Strands Agents SDK: AWS's open-source agent SDK (Python + TS, A2A).

Azure AI Foundry Agent Service (GA; hosted agents July 2026): built on the OpenAI Responses API, wire-compatible. Private networking (BYO VNet), Entra RBAC, MCP over private paths, OTel tracing, evaluations. Models: Azure OpenAI, DeepSeek, xAI, Meta, Claude, Phi. Migration: the preview package `azure-ai-agents` is retired → `AIProjectClient` in `azure-ai-projects`. No markup on the agent layer; model tokens plus tools. Microsoft Agent Framework 1.0 (GA April 3, 2026) merges AutoGen + Semantic Kernel.

Google Vertex AI Agent Builder (renamed "Gemini Enterprise Agent Platform" on April 22, 2026): ADK (code-first, Python/Go/Java/TS), Agent Studio (low-code), Model Garden (200+ models incl. Claude), Agent Engine (managed runtime), governance. Native A2A, MCP. Pricing: Agent Engine $0.0864/vCPU-h + $0.0090/GB-h (free tier); sessions/Memory Bank $0.25/1000 events; Vertex AI Search ≈ $4/1000 queries.

Anthropic Claude Agent SDK (renamed from the Claude Code SDK): built-in tools (Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch), subagents, lifecycle hooks, skills, MCP deeply integrated; Python + TS. Ideal when already working with Claude Code.

OpenAI Agents SDK + Responses API: the Assistants API is deprecated — hard sunset August 26, 2026; successor is the Responses API (since March 11, 2025) plus the Conversations API. The Agents SDK (Python + TS) is production-ready: agents, handoffs, tools (functions/MCP/hosted), guardrails, sessions, tracing. The visual Agent Builder/AgentKit is being discontinued (unavailable after November 30, 2026).

## 4. Agent frameworks — maturity
Python, recommended: LangGraph (1.0 GA Oct 2025; graph/state machine, persistence, checkpoints, HITL; Klarna, Uber, Elastic, Replit; steep learning curve), PydanticAI (V1 Sep 2025, V2 June 2026; type-safe, lean, native MCP/A2A, Logfire; the starting point for ~90% of cases), provider-native SDKs.
Python, with caution: CrewAI (fast prototypes, opaque/expensive in multi-agent pipelines), smolagents (minimal, research, not enterprise), LangChain Classic (obsolete as an orchestrator), AutoGen/Semantic Kernel (merged).
TypeScript: Vercel AI SDK v6 (the UI/toolkit layer), Mastra (a full agent framework, Apache 2.0, $22M Series A April 2026), LangGraph.js.

## 5. Standards & building blocks
MCP (Linux Foundation / Agentic AI Foundation, spec 2026-07-28), A2A (v1.0 April 9, 2026, 150+ organizations, SDKs in 5 languages), ACP (IBM/AGNTCY, smaller). Structured outputs: Pydantic/Zod. Observability: Langfuse (open source, self-hostable, part of ClickHouse since Jan 2026), LangSmith, Arize Phoenix, Helicone, Portkey. Gateways: LiteLLM, OpenRouter, Portkey. Vector DBs: pgvector (default up to ~5–50M vectors), Qdrant, Weaviate, Chroma, LanceDB; the DB choice is only ~5–10% of RAG quality.

## 6. Self-hosted / open source
Serving: vLLM, SGLang; TGI in maintenance mode since Dec 11, 2025; Ollama, LM Studio, llama.cpp. Models: Qwen3 family, gpt-oss (20B ≈ 16 GB, 120B ≈ 80 GB), Llama, Mistral, DeepSeek. Hardware: 16 GB → 8–12B; 24 GB → 30B-A3B/32B Q4; 80 GB → 70B FP8 / gpt-oss-120b. When: compliance, high predictable throughput, data sovereignty; not purely for cost; often hybrid.

## 7. GDPR / EU data residency
Hyperscaler EU regions with DPA (residual CLOUD Act risk). EU providers: Mistral, IONOS AI Model Hub, STACKIT, Aleph Alpha, OVHcloud, Scaleway, Exoscale. Self-hosting as the strongest option. Zero data retention on some APIs. Claude EU residency only via Bedrock EU or Vertex EU.

## Blueprints
A — lean Python stack (FastAPI + PydanticAI/LangGraph + Postgres/pgvector + Langfuse + LiteLLM + Docker; models via API or Ollama). B — TypeScript full-stack (Next.js + Vercel AI SDK v6 or Mastra + Postgres/pgvector + Langfuse). C — enterprise on AWS (AgentCore + Strands/LangGraph + Bedrock models + Knowledge Bases + Guardrails, EU geo Frankfurt). D — enterprise on Azure (Foundry Agent Service + Microsoft Agent Framework + Azure OpenAI/Claude + AI Search + private VNet + Entra RBAC). E — maximum data sovereignty/self-hosted (vLLM + Qwen3/gpt-oss + PydanticAI/LangGraph + pgvector + Langfuse + LiteLLM, Docker). Details: `blueprints.md`.

## Recommendations
Own projects: blueprint A; move individual agents to LangGraph once they are real state machines; integrations as MCP servers; `uv`; a CLAUDE.md/AGENTS.md with conventions. Switch to TS (B) only when a project is primarily a streaming chat/React UI and frontend + agent should live in one repo/team.
Consulting/enterprise clients in Germany: Azure/M365 → D; AWS → C; GCP → Vertex/ADK; sovereignty-critical → E or an EU provider. Keep agent logic portable (MCP for tools, framework-agnostic SDKs).
Hype/obsolete in 2026: the Assistants API; AutoGen/Semantic Kernel separately; LangChain Classic as an orchestrator; smolagents for enterprise; excessive multi-agent framing (~40% of "agent" tasks = one model call with structured output); self-hosting purely for cost.
Watch: MCP spec evolution, A2A production readiness, Mastra/PydanticAI maturity, the EU sovereign cloud framework, new open models with strong tool calling.

## Limitations
Prices are orders of magnitude from 2026 sources and change quickly — check provider pricing pages before any calculation. Many framework comparisons come from vendor/consultancy blogs; official sources were preferred. The Diego Vogel article is explicitly "pseudo-scientific" (18 LLM runs) and covers web, not AI, frameworks. A2A is mature as a protocol; real cross-vendor production outside large enterprises is still rare. Individual version/date details from secondary sources vary slightly.
