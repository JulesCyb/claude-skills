---
name: ai-app-architecture
description: Architektur- und Stack-Entscheidung für Apps mit KI-Agenten (LLM-Apps, Agent-Backends, RAG, MCP, Multi-Tenant/Mandanten) auf Basis einer Recherche von 2026-08. Führt ein kurzes Interview, wählt den passenden Blueprint (schlanker Python-Stack, TypeScript-Full-Stack, AWS Bedrock/AgentCore, Azure AI Foundry, self-hosted/DSGVO), erzeugt ADRs und CLAUDE.md und startet optional vom Template-Repo. Immer verwenden, wenn ein neues Projekt mit KI/LLM/Agenten gestartet wird oder jemand nach Tech-Stack, Architektur, Framework-Wahl (PydanticAI, LangGraph, Vercel AI SDK, Mastra, Bedrock, Azure Foundry, Vertex, Claude Agent SDK), Agent-Einbindung per API, Datenzugriff für Agents, Mandantenfähigkeit, Tenant-Isolation/RLS, DSGVO/EU-Hosting oder eine Mobile-App (Android/iOS, Expo/React Native, PWA) als Client eines Agent-Backends fragt – auch wenn nur "neues Projekt anlegen", "wie fange ich an" oder "welchen Stack nehmen wir" gesagt wird. Nicht für reine Datenanalyse-Skripte, einzelne Prompts oder Projekte ohne LLM-Anteil.
metadata:
  version: "1.1.0"
  stand: "2026-08"
  template_repo: "https://github.com/JulesCyb/ai-app-template"
  sprache: "de"
---

# AI-App-Architektur

Bei jedem Projektstart mit KI-Agenten dieselben, belegten Entscheidungen treffen, statt neu zu recherchieren. Ergebnis sind ADRs, eine `CLAUDE.md` und optional ein Projektgerüst aus dem Template-Repo. Die Sprache der Artefakte folgt der Sprache des Nutzers.

## Ablauf

### 1. Kontext klären – ein Fragenblock, nicht nacheinander

Erst das vorhandene Repo lesen (`pyproject.toml`, `package.json`, `docker-compose*.yml`, `README*`, `docs/adr/`) und nichts fragen, was dort schon steht. Dann alle offenen Punkte in **einem** Block stellen (`AskUserQuestion`, wenn verfügbar):

1. **Kontext** – Eigenprojekt/internes Tool oder Kundenprojekt (Enterprise, Compliance, mehrere Teams)?
2. **Mandanten** – nur einer (jetzt), später mehrere, oder von Anfang an mehrere?
3. **Oberfläche** – keine (API/CLI), Web-App mit Chat/Streaming, bestehende UI anbinden, oder zusätzlich Mobile-App (Android/iOS – jetzt oder später)?
4. **Cloud-Vorgabe** – keine, AWS, Azure, GCP, oder EU-Anbieter/self-hosted Pflicht?
5. **Datenschutz** – Standard (EU-Region + AVV), streng (nur EU-Anbieter oder self-hosted), oder unkritisch?
6. **Datenquellen** – relationale Daten, Dokumente (RAG), Fremdsysteme (welche)?
7. **Team und Sprache** – Python, TypeScript, gemischt?

Fehlt eine Antwort, Default annehmen und **benennen**: Eigenprojekt, ein Mandant (aber mandantenfähig gebaut), Web-App, keine Cloud-Vorgabe, EU-Region, Dokumente + DB, Python.

### 2. Blueprint wählen

- Eigenprojekt oder internes Tool, Python-Team → **A** (Python-Backend als API, optional Next.js-Frontend)
- Produkt ist im Kern eine Chat-/React-UI, TS-Team, keine schweren RAG-/Eval-Pipelines → **B**
- Kunde auf AWS → **C** · Kunde auf Azure/M365 → **D** · Kunde auf GCP → Vertex/ADK (analog C/D)
- Datenschutz streng oder Self-Hosting Pflicht → **E**
- Unsicher → **A**, weil portabel; Agent-Logik so schreiben, dass sie später auf C/D/E umzieht.
- Eine Mobile-App ändert den Blueprint nicht: sie ist ein weiterer Client derselben API (Abschnitt "Mobile Clients" in `references/agent-architektur.md`).

Komponenten, Kosten, Lock-in, Wechselkriterien: `references/blueprints.md`.

### 3. Aktualität prüfen – Pflicht

Die Recherche stammt von 2026-08 (`metadata.stand`). Liegt der Projektstart mehr als etwa sechs Monate danach, den Nutzer darauf hinweisen und vor dem Festlegen von Frameworks und Versionen die aktuellen Docs prüfen (Context7 oder `llms.txt` der Projekte, `uv add`/`npm view` für Versionen). Versionen aus den Referenzdateien nie blind pinnen. Prinzipien in diesem Skill altern langsam, Produktnamen und Preise schnell.

Beispiel, warum das nötig ist: Zwischen der Recherche und dem Bau des Template-Repos hat das MCP-Python-SDK von `FastMCP` auf `MCPServer` (Version 2.0) gewechselt.

### 4. Artefakte erzeugen

Immer:
- `docs/adr/0001-architektur.md` nach `assets/adr-template.md` (ausgefülltes Beispiel: `assets/adr-0001-beispiel.md`). Weitere ADRs nur, wenn wirklich entschieden: `0002-mandanten.md`, `0003-modellzugang.md`, `0004-hosting.md`, `0005-mobile.md` (Vorlage `assets/adr-0005-mobile.md`).
- `CLAUDE.md` aus `assets/CLAUDE.md.template` – Platzhalter ausfüllen, nicht Verwendetes streichen, nichts Generisches stehen lassen.

Optional:
- Projektgerüst: Ist `metadata.template_repo` gesetzt, davon starten (`git clone` und `.git` entfernen oder `degit`), Namen, Ports und Platzhalter ersetzen. Sonst minimale Struktur laut Blueprint anlegen.
- Frontend nur bei Blueprint A mit UI oder B; Vorgehen in `references/agent-architektur.md` (Abschnitt Streaming/UI) und `docs/frontend.md` im Template-Repo.
- Mobile-App: erst wenn Frage 3 sie nennt; dann `assets/adr-0005-mobile.md` ausfüllen und die Backend-Pflichten aus dem Abschnitt "Mobile Clients" (echte Auth, API-Verträge, Jobs, Uploads, Push) als Aufgaben in die Übergabe aufnehmen.

Kein Code ohne ADR: erst die Entscheidung dokumentieren, dann bauen.

### 5. Übergabe

Zusammenfassen: gewählter Blueprint, die fünf wichtigsten Entscheidungen, offene Punkte, was wegen Aktualität zu prüfen war. Fragen, ob Erkenntnisse zurück in den Skill gehören (siehe Pflege).

## Grundsätze – gelten in jedem Projekt, unabhängig vom Blueprint

1. Agent-Logik läuft als eigener Backend-Dienst mit API; UI und Agent nie verschmelzen. Modelle über API (Claude/GPT/Bedrock/Azure), nicht lokal – außer Blueprint E.
2. Ein Kontext-Objekt (`tenant_id`, `user_id`, Rollen) wird durch jeden Request, Agent-Lauf, jedes Tool und jeden Hintergrundjob gereicht. Nichts liest globalen Zustand.
3. Jede Tabelle hat `tenant_id`, Postgres Row-Level Security ist an, Embeddings sind Daten. Die App-DB-Rolle ist **kein Superuser** – sonst greift RLS nicht.
4. Agents greifen auf Daten nur über Tools zu, die mit den Rechten des eingeloggten Nutzers laufen. Nie DB-Zugangsdaten ans Modell. Tools geben nur das Nötige zurück, denn alles Zurückgegebene landet im Prompt beim Modellanbieter.
5. Eigene Integrationen als MCP-Server bauen – einmal, dann in Claude Code, im Produkt und auf Managed-Plattformen nutzen.
6. Provider-Abstraktion für Modelle (Framework-Provider oder LiteLLM). Modellwahl, Prompts, Limits und Fremdsystem-Zugänge pro Mandant konfigurierbar, nicht in der `.env`.
7. Observability ab Tag 1 (Langfuse oder OTel-kompatibel) mit Tenant-Tag; Kosten pro Mandant erfassbar.
8. Kein Low-Code als Kern. Keine Secrets im Repo. EU-Region als Default, AVV prüfen.
9. Cache-Schlüssel (Embeddings, Antworten, Prompt-Cache) enthalten die `tenant_id`.
10. Einfach starten: PydanticAI-Agent mit Tools. LangGraph erst, wenn ein Agent eine echte Zustandsmaschine mit Checkpoints oder Human-in-the-Loop braucht. Etwa 40 % der "Agent"-Aufgaben sind ein einzelner Modellaufruf mit Structured Output.

## Referenzen – nur bei Bedarf lesen

- `references/blueprints.md` – Blueprints A–E, Vergleichstabelle, Wechselkriterien. Lesen in Schritt 2.
- `references/agent-architektur.md` – Backend als API, Agent-Runtime eigen vs. managed, Datenzugriff über Tools/MCP, Streaming zur UI, State/Checkpoints, Observability, Hosting, Mobile Clients. Lesen, wenn Backend, UI, Tools oder eine App gebaut werden.
- `references/mandanten.md` – ein vs. mehrere Mandanten, RLS-Muster (SQL), Kontext-Objekt (Python), Entscheidungstabelle. Lesen, sobald Frage 2 beantwortet ist.
- `references/stack-2026-08.md` – Kurzfassung der Recherche: Plattformen (Bedrock/AgentCore, Azure Foundry, Vertex, OpenAI/Anthropic SDKs), Frameworks, Standards (MCP/A2A), Self-Hosting, DSGVO/EU-Anbieter, was veraltet ist. Lesen bei konkreten Framework- oder Plattformfragen.
- `references/recherche-2026-08.md` – vollständiger Recherchebericht mit Quellen. Nur bei Detailfragen.
- `assets/CLAUDE.md.template`, `assets/adr-template.md`, `assets/adr-0001-beispiel.md`, `assets/adr-0005-mobile.md` – Vorlagen für Schritt 4.

## Pflege

Neue Erkenntnisse (bessere Bibliothek, gescheiterte Entscheidung, Preis- oder Produktänderung) in die passende Referenzdatei schreiben, `metadata.version` und `metadata.stand` anpassen, Changelog in `README.md` ergänzen. Nach größeren Änderungen die Testprompts in `evals/evals.json` erneut laufen lassen (Claude Code: skill-creator-Plugin) und prüfen, dass der Skill weiterhin bei "neues KI-Projekt" anspringt und bei "CSV analysieren" nicht.
