# Agent-Architektur: Backend als API, Datenzugriff, Streaming, State

## Die drei Schichten

```
Web-Oberfläche (Next.js/React, Streaming-Chat)
        │  HTTP/SSE
Agent-Backend (deine API: FastAPI + PydanticAI/LangGraph)
   ├── Modell-API (Claude, GPT, Bedrock, Azure – über Provider-Abstraktion/LiteLLM)
   ├── Daten (Postgres + pgvector, Objektspeicher) – nur über Tools mit Nutzerrechten
   └── Tools/MCP-Server (eigene Systeme, Fremd-APIs)
Langfuse/OTel zeichnet jeden Lauf auf.
```

Die UI ist dumm: sie schickt Nachrichten und rendert den Stream. Die Intelligenz sitzt im Backend. Modelle sind austauschbare externe Dienste.

## "Agenten per API" – zwei Varianten, beide möglich

**Variante 1 – eigener Backend-Dienst (Default).** Agent-Logik läuft in FastAPI (Docker, EU-Server oder Container-Dienst). Das Backend stellt Endpunkte wie `POST /agents/assistant/run` bereit, ruft selbst nur die Modell-API auf. Schlank, portabel, günstig. Für lange Läufe: Job-Queue (z. B. Postgres-basiert oder Redis/RQ), Status-Endpunkt, Ergebnisse in DB.

**Variante 2 – Managed-Plattform.** Der Agent läuft auf Bedrock AgentCore, Azure Foundry Agent Service oder Vertex Agent Engine; die App spricht deren API an. Lohnt sich bei vielen langlaufenden Agents, Enterprise-Identity, Session-Isolation, Auditing, oder wenn der Kunde die Plattform vorgibt. Dieselbe PydanticAI-/Strands-/LangGraph-Logik zieht dorthin um.

Regel: Logik so schreiben, dass sie nicht am Hosting klebt – Framework-Agent + Tools + Kontext-Objekt, keine plattformspezifischen Aufrufe im Agent-Kern.

## Datenzugriff der Agents

- Der Agent bekommt nie rohe DB-Zugangsdaten. Er bekommt **Tools**: "suche in den Dokumenten des Nutzers", "hol die Umsätze von Monat X", "lege Vorgang an".
- Jedes Tool ist eine Funktion im Backend, die mit den Rechten des eingeloggten Nutzers läuft: `tenant_id`/`user_id` kommen aus dem Kontext-Objekt, RLS filtert in der DB, das Tool prüft Rollen.
- Dokumente per RAG aus pgvector (Filter auf `tenant_id`), strukturierte Daten per SQL im Repository, Fremdsysteme über MCP-Server.
- Alles, was ein Tool zurückgibt, landet im Prompt und damit beim Modellanbieter → nur das Nötige zurückgeben, EU-Region und AVV wählen, ggf. Zero-Data-Retention-Optionen nutzen.
- Prompt-Injection über Daten einkalkulieren: Tool-Ergebnisse sind Daten, keine Anweisungen; schreibende Tools brauchen Bestätigung (Human-in-the-Loop) oder enge Guardrails.

## MCP-Server als Integrationsschicht

Ein MCP-Server pro Datenquelle/Fremdsystem, mit denselben Tool-Funktionen wie im Backend (gemeinsames Modul, zwei Einstiegspunkte). Nutzen: Claude Code beim Entwickeln, das Produkt (PydanticAI kann MCP-Server als Toolset einbinden), Claude Desktop, später AgentCore/Foundry – ohne Neuschreiben. Im Produkt läuft der MCP-Server mit Auth (OAuth/Token) und Tenant-Kontext; lokal für Entwicklung per stdio.

Achtung Aktualität: Das MCP-Python-SDK 2.0 verwendet `from mcp.server.mcpserver import MCPServer` (früher `FastMCP`). Vor dem Bauen die aktuelle SDK-Doku prüfen.

## Streaming zur Oberfläche

- Backend streamt per Server-Sent Events. Mit PydanticAI: `agent.run_stream(...)` und `stream_text(delta=True)` für reinen Text; für eine Vercel-AI-SDK-kompatible Chat-UI `VercelAIAdapter.dispatch_request(request, agent=..., deps=..., sdk_version=6)` – dann funktionieren `useChat`-Hooks im Next.js-Frontend direkt gegen das FastAPI-Backend. Alternativ AG-UI-Adapter für generische Agent-UIs.
- Frontend-Scaffold zum Projektzeitpunkt mit `npx create-next-app@latest` und `npm i ai @ai-sdk/react` (Versionen aktuell prüfen), Chat-Komponente zeigt auf `/api/chat` des Backends (Proxy oder direkte URL, CORS beachten).
- Tool-Aufrufe im Stream anzeigen (der Adapter liefert Tool-Events), damit Nutzer sehen, was der Agent tut.

## State, Speicher, Zustandsmaschinen

- Kurzzeit: Nachrichtenverlauf pro Konversation in Postgres (`conversations`, `messages` mit `tenant_id`).
- Langzeit: nur, wenn nötig – Zusammenfassungen/Fakten pro Nutzer, klar getrennt, löschbar (DSGVO).
- Zustandsmaschine (definierte Schritte, Wiederaufnahme, Freigaben): LangGraph mit Postgres-Checkpointer. Vorher prüfen, ob ein PydanticAI-Agent mit Tools reicht.
- Human-in-the-Loop: Workflow pausiert an einem Knoten, wartet auf Freigabe (UI-Aktion → Endpoint), läuft weiter; nur sauber mit gespeichertem Zustand.

## Observability

- Langfuse (self-hosted oder Cloud) über OpenTelemetry: PydanticAI-Instrumentierung an, `tenant_id`/`user_id` als Trace-Attribute, Kosten pro Trace. Alternativen: LangSmith, Arize Phoenix, Logfire.
- Von Tag 1 – nicht nachrüsten. Ohne Traces debuggt man Agents im Blindflug.
- Audit-Log ab mehreren Mandanten: wer hat welchen Agent mit welchen Daten wann laufen lassen.

## Hosting-Standard für Blueprint A

- Docker Compose: `api`, `postgres` (pgvector-Image), optional `litellm`, `langfuse` (offizielle Compose-Datei von Langfuse einbinden – die Version 3 braucht ClickHouse/Redis/MinIO), optional `minio`.
- Zwei DB-Rollen: Migrationsrolle (Owner) und App-Rolle (kein Superuser, `NOBYPASSRLS`). Der Superuser aus dem Postgres-Image umgeht RLS – die App darf sich nie damit verbinden.
- Secrets per `.env` (nicht im Repo) oder Secret-Manager; pro Mandant verschlüsselt in der DB.
- EU-Standort; für Kunden mit strenger Vorgabe siehe Blueprint E.
