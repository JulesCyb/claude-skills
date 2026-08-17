# Blueprints A–E (Stand 2026-08)

Fünf Stack-Zusammenstellungen, die die Recherche als tragfähig identifiziert hat. Der Blueprint legt Hosting, Sprache und Plattform fest – die Grundsätze aus `SKILL.md` gelten in allen fünf.

## Blueprint A – Schlanker Python-Stack (Default für Eigenprojekte und interne Tools)

**Komponenten**
- Backend/API: FastAPI (async), Paketmanager `uv`
- Agent-Logik: PydanticAI (typsichere Agents, Structured Output, native MCP); LangGraph nur für Agents mit echter Zustandsmaschine (Checkpoints, Human-in-the-Loop, Wiederaufnahme)
- Daten: PostgreSQL + pgvector (Daten, Metadaten und Embeddings in einer DB), Row-Level Security an
- Modelle: per API – Claude/GPT/Gemini direkt, über Bedrock/Azure in EU-Region, oder mit LiteLLM als Gateway (virtuelle Keys, Budgets, Fallbacks, Anbieterwechsel per Konfigzeile). Ollama/vLLM nur für Entwicklung oder Blueprint E.
- Observability: Langfuse (self-hosted oder Cloud), OTel-basiert, mit Tenant-Tag
- Integrationen: eigene MCP-Server für Fremdsysteme
- Betrieb: Docker Compose auf EU-Server (Hetzner, IONOS, netcup …) oder Container-Dienst; Objektspeicher S3-kompatibel (MinIO/Hetzner) für Dateien
- Frontend (optional): Next.js/React mit Vercel AI SDK, das den FastAPI-Stream konsumiert; PydanticAI bringt Adapter für das Vercel-AI-SDK-Streamformat und AG-UI mit

**Stärken:** passt zu Python-Basis, sehr gut mit Claude Code scaffoldbar (dichte Konventionen, Pydantic-Typisierung), null Vendor-Lock-in, DSGVO-fähig, günstig (Infra + Tokens).
**Schwächen:** kein natives Frontend; für UI zweite Sprache (dünnes TS-Frontend).
**Kosten:** Server + Tokens; Langfuse und LiteLLM self-hosted kostenlos.
**Lock-in:** minimal – jede Komponente einzeln tauschbar.

## Blueprint B – TypeScript-Full-Stack (wenn das Produkt eine Chat-/React-App ist)

**Komponenten**
- Next.js + Vercel AI SDK (v6: Streaming, Tool-Loop-Agents, Structured Output via Zod, MCP) – oder Mastra, wenn echte Workflows, Memory über Sitzungen, Evals, RAG gebraucht werden
- Postgres + pgvector, Langfuse
- Hosting: Vercel-Plattform *oder* Cloudflare/Railway/Fly/self-hosted (Docker, Coolify) – das AI SDK ist eine Bibliothek und braucht die Vercel-Plattform nicht

**Wann B statt A:** Frontend + Agent sollen in einem Repo und einer Sprache leben, die Streaming-UI steht im Zentrum, das Team ist TS-stark. Sobald ML-schwere Arbeit dazukommt (Fine-Tuning, komplexe Retrieval-Pipelines, Evals), Python-Backend hinzunehmen (A+B-Kombination: Python-Backend, TS-Frontend).
**Stärken:** eine Sprache über den ganzen Stack, End-to-End-Typsicherheit, sehr schnelle Time-to-MVP.
**Schwächen:** ML-Ökosystem dünner; LangGraph.js hinkt Python hinterher.
**Lock-in:** AI SDK keiner; Vercel-*Plattform* framework-shaped Lock-in (ISR, Middleware, Fluid Compute) und Preissprünge bei Bandbreite.

## Blueprint C – Enterprise auf AWS

**Komponenten**
- Amazon Bedrock AgentCore (GA seit 2025-10-13): Runtime (bis 8 h, MicroVM-Session-Isolation), Gateway (Tools/MCP), Memory, Identity, Observability, Browser, Code Interpreter, Policy/Evaluations
- Agent-Code: Strands Agents SDK (AWS, Python/TS) oder LangGraph/PydanticAI – AgentCore ist framework- und modellagnostisch
- Modelle: Bedrock (Claude, Nova, OpenAI-Modelle, Llama, Mistral …), EU-Geo-Cross-Region-Inference (Frankfurt/Irland/Paris)
- Wissen: Bedrock Knowledge Bases; Guardrails
- Standards: MCP und A2A nativ

**Preismodell (Größenordnung, offizielle AgentCore-Preisseite 2026):** Runtime/Browser/Code Interpreter ca. 0,0895 $/vCPU-Stunde + 0,00945 $/GB-Stunde (nur aktive CPU), Gateway 0,005 $/1000 Calls, Memory 0,25 $/1000 Events (Langzeit 0,75 $/1000 Records/Monat). Modell-Tokens immer zusätzlich – der größte Block.
**EU/DSGVO:** AgentCore vollständig in Frankfurt; AVV vorhanden; CLOUD-Act-Restrisiko wie bei allen US-Hyperscalern.
**Lock-in:** mittel bis hoch (AgentCore-Dienste), abgemildert durch framework-/modellagnostische Agent-Logik.
**Wann:** Kunde ist auf AWS, braucht Enterprise-Security, Session-Isolation, lange Läufe, Auditing.

## Blueprint D – Enterprise auf Azure (in deutschen Unternehmen der häufigste Fall)

**Komponenten**
- Azure AI Foundry Agent Service (baut auf der OpenAI Responses API auf, wire-kompatibel), private Networking (BYO VNet), Entra RBAC, MCP über private Pfade, OTel-Tracing, Evaluations
- Agent-Code: Microsoft Agent Framework 1.0 (GA 2026-04; Zusammenführung von AutoGen und Semantic Kernel, Python + .NET, MCP + A2A nativ) oder Responses-API-kompatible Agents (OpenAI Agents SDK)
- Modelle: Azure OpenAI, Claude in Foundry, DeepSeek, Llama, Phi u. a.; Suche: Azure AI Search
- Kein Aufschlag auf die Agent-Schicht: Kosten = Modell-Tokens + genutzte Tools (Bing, AI Search, Logic Apps)

**EU/DSGVO:** EU-Regionen, AVV, in DE etablierteste Enterprise-Plattform.
**Lock-in:** hoch (Azure), Migration durch Responses-API-Kompatibilität erleichtert.
**Wann:** Kunde ist auf Azure/M365 – dann ist D fast immer der pragmatische Default.
**GCP-Analogon:** Vertex AI / Gemini Enterprise Agent Platform mit ADK (code-first, Python/Go/Java/TS), Agent Engine als managed Runtime (ca. 0,0864 $/vCPU-h + 0,009 $/GB-h), Model Garden inkl. Claude, A2A nativ.

## Blueprint E – Maximal DSGVO-freundlich / self-hosted

**Komponenten**
- Modell-Serving: vLLM (Produktion, Durchsatz, continuous batching) oder SGLang; Ollama nur Prototyp/Homelab
- Modelle mit Tool-Calling: Qwen3-Familie (30B-A3B als Sweet Spot auf einer 24-GB-GPU), gpt-oss 20B/120B (Apache 2.0), Llama, Mistral; Flaggschiffe (235B+) brauchen Multi-GPU
- Agent-Logik: PydanticAI oder LangGraph, pgvector, Langfuse self-hosted, LiteLLM self-hosted (Daten bleiben im Haus)
- Alles in Docker/Kubernetes auf eigener oder gemieteter EU-Hardware; optional EU-Anbieter (Mistral, IONOS AI Model Hub, STACKIT) für Lastspitzen

**Hardware grob:** 16 GB VRAM → 8–12B-Modell; 24 GB → 30B-A3B/32B (Q4); 80 GB (H100) → 70B FP8 / gpt-oss-120b.
**Stärken:** volle Datenhoheit, keine AVV mit US-Anbietern nötig, keine Token-Kosten.
**Schwächen:** Ops-Aufwand, Hardware-Invest, Modelle unter Frontier-Niveau; Kosten-Break-even gegenüber APIs erst bei sehr hohem Volumen.
**Wann:** Public Sector, Gesundheit, Verträge mit EU-only-Klausel, hoher planbarer Durchsatz.

## Vergleich

| Kriterium | A Python schlank | B TS Full-Stack | C AWS AgentCore | D Azure Foundry | E Self-hosted |
|---|---|---|---|---|---|
| Beste für | Eigenprojekte, interne Tools, Produkt mit Python-Backend | Chat-/React-Produkte | AWS-Enterprise | Azure/DE-Enterprise | Max. DSGVO |
| Claude-Code-Eignung | sehr hoch | hoch | mittel | mittel | hoch |
| Time-to-MVP | schnell | sehr schnell | mittel | mittel | langsam |
| Lock-in | minimal | SDK keiner / Plattform mittel | mittel–hoch | hoch | keiner |
| DSGVO/EU | gut | gut | gut (EU-Geo) | gut (EU + AVV) | maximal |
| Kosten | Tokens + Infra | Tokens + Hosting | Verbrauch + Tokens | Tokens + Tools | Hardware + Ops |
| Skalierung/Governance | selbst bauen | selbst bauen | Enterprise-grade | Enterprise-grade | selbst bauen |
| MCP/A2A | ja (Framework) | ja (SDK/Mastra) | ja nativ | ja nativ | ja (Framework) |

## Wechselkriterien

- **A → A + Next.js-Frontend:** sobald eine Web-UI mit Streaming gebraucht wird. Backend bleibt.
- **A → B:** nur wenn das Backend bewusst in TypeScript sein soll (TS-Team) und keine ML-schwere Arbeit ansteht.
- **A → C/D:** wenn Enterprise-Anforderungen kommen (Identity, Session-Isolation, viele langlaufende Agents, Auditing) oder der Kunde die Cloud vorgibt. Agent-Logik in PydanticAI/Strands/LangGraph zieht mit; Tools als MCP-Server ebenfalls.
- **A → E:** wenn Datenschutz streng wird oder Volumen so hoch, dass Self-Hosting rechnet.
- **PydanticAI → LangGraph (einzelne Agents):** wenn ein Ablauf definierte Schritte, Wiederaufnahme nach Absturz/Wartezeit, Audit-Trail oder menschliche Freigabe braucht.
- **pgvector → Qdrant/Weaviate:** erst bei sehr großen Datenmengen oder metadaten-schwerem Filtering; die DB-Wahl macht nur 5–10 % der RAG-Qualität aus (Chunking, Embedding-Modell, Retrieval-Pipeline zählen mehr).
