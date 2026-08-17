# ADR-0001: Architektur und Stack für <Projektname>

- **Status:** akzeptiert
- **Datum:** 2026-08-17
- **Entscheider:** <Name>
- **Skill-Stand:** ai-app-architecture v1.0.0 (Recherche 2026-08)

## Kontext

Eigenprojekt, das zu einem Produkt mit Weboberfläche werden soll. Zunächst ein Mandant (wir selbst), später wahrscheinlich mehrere Kunden mit jeweils eigenen Daten. Die Agenten sollen als Backend-Dienst über eine API eingebunden werden und Zugriff auf Dokumente (RAG) und relationale Daten haben; Modelle laufen nicht lokal. Keine Cloud-Vorgabe; EU-Datenhaltung erwünscht, DSGVO ist Bonus, kein Muss. Team: Python-stark, Entwicklung primär mit Claude Code.

## Optionen

1. **Blueprint A – Python-Backend als API + Next.js-Frontend**: FastAPI + PydanticAI, Postgres/pgvector, Langfuse, LiteLLM, Docker; Modelle per API in EU-Region. Vorteile: passt zum Team, kein Lock-in, sehr gut mit Claude Code scaffoldbar. Nachteil: zwei Sprachen (dünnes TS-Frontend).
2. **Blueprint B – TypeScript-Full-Stack** (Next.js + Vercel AI SDK/Mastra): eine Sprache, schnellste UI. Nachteil: Backend-Team ist Python; ML-schwere Arbeit dünner.
3. **Blueprint C/D – Managed-Plattform** (AgentCore/Foundry): Enterprise-Governance, aber Lock-in und Overhead, den ein Eigenprojekt jetzt nicht braucht.

## Entscheidung

Wir wählen **Blueprint A**: FastAPI + PydanticAI (LangGraph nur für Agents mit echter Zustandsmaschine), PostgreSQL 17 + pgvector mit Row-Level Security, Langfuse (self-hosted) für Tracing, LiteLLM als Modell-Gateway, Docker Compose auf einem EU-Server. Frontend: Next.js mit Vercel AI SDK gegen den FastAPI-Stream (PydanticAI-Vercel-Adapter). Mandantenfähig von Tag 1 (`tenant_id` überall, RLS, Kontext-Objekt, `tenant_settings`), aber nur ein Mandant angelegt.

## Konsequenzen

- Positiv: portabel; einzelne Komponenten (Modell, Gateway, Observability) einzeln tauschbar; zweiter Mandant per Insert; Umzug auf AgentCore/Foundry später möglich, weil Agent-Logik framework-basiert bleibt und Tools als MCP-Server vorliegen.
- Negativ: zwei Sprachen; Betrieb (Compose, Backups, Updates) liegt bei uns; Modell-Tokens sind der größte Kostenblock.
- Schwerer wird: Wechsel auf DB-pro-Mandant (geht nur über die Repository-Schicht – deshalb Pflicht).

## Überprüfen, wenn …

- ein Kunde physische Datentrennung oder eigenes Cloud-Konto (BYOK) verlangt → ADR-0002 (Mandanten-Isolation), ADR-0003 (Modellzugang)
- Enterprise-Anforderungen (Identity, Session-Isolation, viele langlaufende Agents) kommen → Blueprint C/D prüfen
- die Streaming-UI zum eigentlichen Produkt wird und das Backend dünn bleibt → Blueprint B prüfen
- die Recherche älter als sechs Monate ist → Framework- und Preisstand neu prüfen
