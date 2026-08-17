# Recherchebericht: Beste Tech-Stacks für KI-/Agent-Apps 2026 (Stand 2026-08)

Ursprüngliche Fragestellung: Welche Stacks für Apps mit KI taugen 2026, speziell mit sinnvoller Einbindung von Agents – für Eigenprojekte und Beratungskontext, self-hosted und Managed Cloud (u. a. AWS Bedrock), DSGVO als Bonus, kein Low-Code, entwickelt primär mit KI-Coding-Agents in der CLI (Claude Code). Quellenliste am Ende von `stack-2026-08.md`.

## TL;DR
- Für Eigenprojekte ist ein schlanker Python-Stack die richtige Wahl (FastAPI + PydanticAI oder LangGraph + Postgres/pgvector + Langfuse + Docker, Modelle via API-Gateway/LiteLLM oder lokal via Ollama/vLLM). Passt zu Python-Basis, ist mit Claude Code exzellent scaffoldbar, kein Vendor-Lock-in. TypeScript (Next.js + Vercel AI SDK oder Mastra) lohnt nur, wenn das Produkt selbst eine React-/Chat-UI ist und Frontend + Agent in einer Sprache/Repo leben sollen.
- Für deutsche Consulting-/Enterprise-Kunden entscheidet die vorhandene Cloud, nicht das „beste" Framework: Azure AI Foundry Agent Service (in DE dominant), AWS Bedrock AgentCore oder Google Vertex/Gemini Enterprise Agent Platform – alle drei GA 2025/2026, alle mit EU-Regionen (Frankfurt), MCP- und A2A-Support. DSGVO-maximal ist ein self-hosted Stack (vLLM + offene Modelle wie Qwen3/gpt-oss) oder ein EU-Anbieter (Mistral, IONOS AI Model Hub, STACKIT).
- Standardschicht ist entschieden: MCP (Model Context Protocol) ist der De-facto-Standard für Tool-Anbindung (Linux-Foundation-Governance, laut MCP-Blog vom 9. Dez. 2025 über 97 Mio. monatliche SDK-Downloads und ~10.000 aktive Server), A2A für Agent-zu-Agent-Kommunikation. Tools als MCP-Server bauen, dann sind sie framework- und anbieterportabel. Nicht mehr neu aufsetzen: OpenAI Assistants API (Sunset 26. August 2026), reines LangChain-„Classic" als Orchestrator, AutoGen/Semantic Kernel getrennt (in Microsoft Agent Framework zusammengeführt).

## Kernbefunde
1. Sprache: Python bleibt Default für Agent-Logik, TypeScript gewinnt an der Produkt-/UI-Kante. Die AI/ML-Bibliothekstiefe hat einen mehrjährigen Vorsprung; für RAG-Pipelines, Evals und Orchestrierung ist Python schneller am Ziel. TypeScript ist überlegen, wenn das Produkt eine Next.js-/React-App mit Streaming-Chat ist. Beide sind für KI-Coding-Agents die stärksten Ökosysteme, weil sie im Trainingskorpus dominieren.
2. Framework-Konsolidierung: In Python haben sich LangGraph (stateful/graph-basiert, Produktions-Default) und PydanticAI (typsicher, schlank, schneller Start) als die zwei tragenden Optionen herausgebildet; dazu die anbieternativen SDKs (OpenAI Agents SDK, Claude Agent SDK, Google ADK, AWS Strands). In TypeScript sind Vercel AI SDK (v6) und Mastra die Pfeiler.
3. MCP + A2A sind Infrastruktur-Standard, nicht Hype. Neue MCP-Spec (2026-07-28) mit stateless Core.
4. Managed-Plattformen zahlt man nach Verbrauch plus Modell-Tokens. AgentCore und Vertex Agent Engine ohne Grundgebühr auf die Orchestrierung; Azure Foundry Agent Service ohne Aufschlag auf die Agent-Schicht. Der größte Kostenblock sind immer die Modell-Tokens.
5. Self-Hosting lohnt bei Compliance und hohem, planbarem Durchsatz – selten rein aus Kostengründen. vLLM (und SGLang) sind der Produktions-Serving-Stack; Ollama ist für Prototyp/Homelab. Tool-Calling-fähige offene Modelle 2026: Qwen3-Familie, gpt-oss (20B/120B), Llama, Mistral, DeepSeek.

## 1. Ausgangsartikel – Einordnung
Der Artikel von Diego Vogel (diego.works, Mai 2026) ist ein bewusst „pseudo-wissenschaftliches" Experiment: ein Prompt, 3 LLMs, je 6 Läufe. Leaderboard: Rails+Hotwire, Next.js+TypeScript, Phoenix+LiveView vorne. Einschränkung: Er behandelt Web-Frameworks für agentengestützte Web-Entwicklung, nicht AI-/Agent-Frameworks. Übertragbare Erkenntnisse: (a) Konventions-Dichte im Trainingskorpus schlägt „explizit vs. implizit"; (b) statische Typisierung ist Tiebreaker, kein Gate; (c) jedes LLM hat einen Bias (Claude→Phoenix, ChatGPT→Rails, Gemini→Next.js); (d) AGENTS.md/CLAUDE.md und gepinnte Doku heben die Erfolgsquote messbar.

Der Hackmamba/dev.to-Artikel (Mai 2026) definiert die AI-Stack-Schichten (App/UI, Backend, Orchestrierung, Retrieval/Memory, Modell, Daten, Eval/Monitoring, Deployment) und zeigt empirisch, dass Python/JS/TS deutlich stabilere LLM-generierte Ergebnisse liefern als Flutter/Swift/Kotlin. Kernregel: „AI-Logik dort, wo das Modell am stärksten ist" – Python/TS-Backend, egal welche UI.

## 2. Python vs. TypeScript
Python – Stärken: tiefstes AI-Ökosystem (PyTorch, Hugging Face, vLLM, LangGraph, PydanticAI, LlamaIndex, DSPy); Forschung zuerst in Python; beste Wahl für RAG, Evals, Modell-Experimente, Daten-Pipelines; Async über asyncio/FastAPI ausgereift; für KI-Coding-Agents exzellent. Schwächen: kein natives Frontend; Paketmanagement historisch fragil – `uv` hat das weitgehend gelöst; Runtime-Typfehler ohne Pydantic/Type-Hints.

TypeScript – Stärken: eine Sprache über den ganzen Stack; Streaming-Chat-UI, Edge-Deployment, End-to-End-Typsicherheit; Compiler fängt Breaking Changes bei SDK-Migrationen; laut GitHub Octoverse 2025 im August 2025 erstmals meistgenutzte Sprache auf GitHub. Schwächen: ML-schwere Arbeit dünner; LangGraph.js hinkt Python hinterher.

Typische Kombination: Python-Backend + TypeScript-Frontend. Für interne Tools ohne anspruchsvolle UI reicht Python allein.

Vercel: Vercel AI SDK (quelloffene TS-Bibliothek, v6 Juni 2026, einheitliche Provider-API, Streaming, Structured Output via Zod, Tool-Calling, `Agent`-Abstraktion, durable Workflow-Agents; läuft überall) vs. Vercel-Plattform (kostenpflichtiges Hosting, optimiert für Next.js; Lock-in über frameworkgebundene Features, Preissprünge bei Bandbreite). Alternativen: Cloudflare, Netlify, Railway, Render, Fly.io, self-hosted via Docker/Coolify.

## 3. Managed Cloud / Enterprise-Plattformen
AWS Bedrock AgentCore (GA 13. Oktober 2025): Runtime (bis 8 h, MicroVM-Session-Isolation), Gateway, Memory, Browser, Code Interpreter, Identity, Observability, Policy und Evaluations (Preview seit Dez 2025). Framework-agnostisch (LangGraph, CrewAI, LlamaIndex, Strands, Google ADK, OpenAI Agents SDK); MCP- und A2A-Support; jedes Foundation-Modell. Preis: Runtime/Browser/Code Interpreter je 0,0895 $/vCPU-h und 0,00945 $/GB-h (nur aktive CPU); Gateway 0,005 $/1000 API-Calls, semantische Suche 0,025 $/1000, Tool-Indexierung 0,02 $/100 Tools/Monat; Memory 0,25 $/1000 Events, Langzeit 0,75 $/1000 Records/Monat. EU/DSGVO: AgentCore vollständig in Frankfurt; EU-Geo-Cross-Region-Inference hält Daten in EU-Regionen. Strands Agents SDK: AWS' quelloffenes Agent-SDK (Python + TS, A2A).

Azure AI Foundry Agent Service (GA; hosted agents Juli 2026): baut auf der OpenAI Responses API auf, wire-kompatibel. Private Networking (BYO VNet), Entra RBAC, MCP über private Pfade, OTel-Tracing, Evaluations. Modelle: Azure OpenAI, DeepSeek, xAI, Meta, Claude, Phi. Migration: Preview-Paket `azure-ai-agents` entfällt → `AIProjectClient` in `azure-ai-projects`. Kein Aufschlag auf die Agent-Schicht; Modell-Tokens plus Tools. Microsoft Agent Framework 1.0 (GA 3. April 2026) führt AutoGen + Semantic Kernel zusammen.

Google Vertex AI Agent Builder (seit 22. April 2026 „Gemini Enterprise Agent Platform"): ADK (code-first, Python/Go/Java/TS), Agent Studio (low-code), Model Garden (200+ Modelle inkl. Claude), Agent Engine (managed Runtime), Governance. Native A2A, MCP. Preis: Agent Engine 0,0864 $/vCPU-h + 0,0090 $/GB-h (Freikontingent); Sessions/Memory Bank 0,25 $/1000 Events; Vertex AI Search ~4 $/1000 Queries.

Anthropic Claude Agent SDK (umbenannt vom Claude Code SDK): eingebaute Tools (Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch), Subagenten, Lifecycle-Hooks, Skills, MCP tief integriert; Python + TS. Ideal, wenn ohnehin mit Claude Code gearbeitet wird.

OpenAI Agents SDK + Responses API: Assistants API deprecated – Hard-Sunset 26. August 2026; Nachfolger Responses API (seit 11. März 2025) plus Conversations API. Agents SDK (Python + TS) produktionsreif: Agents, Handoffs, Tools (Funktionen/MCP/hosted), Guardrails, Sessions, Tracing. Visueller Agent Builder/AgentKit wird eingestellt (nicht mehr verfügbar ab 30. November 2026).

## 4. Agent-Frameworks – Reifegrad
Python empfehlenswert: LangGraph (1.0 GA Okt 2025; Graph/State-Machine, Persistenz, Checkpoints, HITL; Klarna, Uber, Elastic, Replit; steile Lernkurve), PydanticAI (V1 Sep 2025, V2 Juni 2026; typsicher, schlank, native MCP/A2A, Logfire; Startpunkt für ~90 % der Fälle), anbieternative SDKs.
Python mit Vorsicht: CrewAI (schneller Prototyp, opak/teuer bei Multi-Agent-Pipelines), smolagents (minimal, Research, nicht Enterprise), LangChain Classic (als Orchestrator veraltet), AutoGen/Semantic Kernel (zusammengeführt).
TypeScript: Vercel AI SDK v6 (UI-/Toolkit-Schicht), Mastra (voller Agent-Framework, Apache 2.0, Series A 22 M$ April 2026), LangGraph.js.

## 5. Standards & Bausteine
MCP (Linux Foundation / Agentic AI Foundation, Spec 2026-07-28), A2A (v1.0 9. April 2026, 150+ Organisationen, SDKs in 5 Sprachen), ACP (IBM/AGNTCY, kleiner). Structured Outputs: Pydantic/Zod. Observability: Langfuse (Open Source, self-hostbar, seit Jan 2026 Teil von ClickHouse), LangSmith, Arize Phoenix, Helicone, Portkey. Gateways: LiteLLM, OpenRouter, Portkey. Vektor-DBs: pgvector (Default bis ~5–50 Mio. Vektoren), Qdrant, Weaviate, Chroma, LanceDB; DB-Wahl nur ~5–10 % der RAG-Qualität.

## 6. Self-hosted / Open Source
Serving: vLLM, SGLang; TGI seit 11. Dez 2025 Maintenance-Modus; Ollama, LM Studio, llama.cpp. Modelle: Qwen3-Familie, gpt-oss (20B ~16 GB, 120B ~80 GB), Llama, Mistral, DeepSeek. Hardware: 16 GB → 8–12B; 24 GB → 30B-A3B/32B Q4; 80 GB → 70B FP8 / gpt-oss-120b. Wann: Compliance, hoher planbarer Durchsatz, Datenhoheit; nicht rein aus Kostengründen; oft Hybrid.

## 7. DSGVO/EU-Datenresidenz
Hyperscaler EU-Regionen mit AVV/DPA (CLOUD-Act-Restrisiko). EU-Anbieter: Mistral, IONOS AI Model Hub, STACKIT, Aleph Alpha, OVHcloud, Scaleway, Exoscale. Self-Hosting als stärkste Option. Zero-Data-Retention bei manchen APIs. Claude EU-Residency nur via Bedrock EU oder Vertex EU.

## Blueprints
A – Schlanker Python-Stack (FastAPI + PydanticAI/LangGraph + Postgres/pgvector + Langfuse + LiteLLM + Docker; Modelle via API oder Ollama). B – TypeScript-Full-Stack (Next.js + Vercel AI SDK v6 oder Mastra + Postgres/pgvector + Langfuse). C – Enterprise auf AWS (AgentCore + Strands/LangGraph + Bedrock-Modelle + Knowledge Bases + Guardrails, EU-Geo Frankfurt). D – Enterprise auf Azure (Foundry Agent Service + Microsoft Agent Framework + Azure OpenAI/Claude + AI Search + private VNet + Entra RBAC). E – Maximal DSGVO-freundlich/self-hosted (vLLM + Qwen3/gpt-oss + PydanticAI/LangGraph + pgvector + Langfuse + LiteLLM, Docker). Details: `blueprints.md`.

## Empfehlungen
Eigenprojekte: Blueprint A; einzelne Agents zu LangGraph, sobald echte Zustandsmaschinen; Integrationen als MCP-Server; `uv`; CLAUDE.md/AGENTS.md mit Konventionen. TS-Wechsel (B) erst, wenn ein Projekt primär eine Streaming-Chat-/React-UI ist und Frontend + Agent in einem Repo/Team leben sollen.
Consulting-/Enterprise-Kunden in DE: Azure/M365 → D; AWS → C; GCP → Vertex/ADK; souveränitätskritisch → E oder EU-Anbieter. Agent-Logik portabel halten (MCP für Tools, framework-agnostische SDKs).
Hype/veraltet 2026: Assistants API; AutoGen/Semantic Kernel getrennt; LangChain Classic als Orchestrator; smolagents für Enterprise; übermäßiges Multi-Agent-Framing (~40 % der „Agent"-Tasks = ein Modellaufruf mit Structured Output); Self-Hosting rein aus Kostengründen.
Beobachten: MCP-Spec-Evolution, A2A-Produktionsreife, Mastra/PydanticAI-Reife, EU-Sovereign-Cloud-Framework, neue offene Modelle mit starkem Tool-Calling.

## Einschränkungen
Preise sind Größenordnungen aus 2026er Quellen und ändern sich schnell – vor Kalkulation Anbieter-Preisseiten prüfen. Viele Framework-Vergleiche stammen von Vendor-/Consultancy-Blogs; offizielle Quellen wurden bevorzugt. Der Diego-Vogel-Artikel ist explizit „pseudo-wissenschaftlich" (18 LLM-Läufe) und behandelt Web-, nicht AI-Frameworks. A2A ist am Protokoll reif, echte Cross-Vendor-Produktion außerhalb großer Enterprises noch selten. Einzelne Versions-/Datumsangaben aus Sekundärquellen variieren leicht.
