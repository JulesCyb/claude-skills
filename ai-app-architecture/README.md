# ai-app-architecture – Claude-Code-Skill

Ein Skill, der bei jedem Projektstart mit KI-Agenten dieselben, belegten Architekturentscheidungen trifft: kurzes Interview → Blueprint (A schlanker Python-Stack, B TypeScript-Full-Stack, C AWS Bedrock/AgentCore, D Azure AI Foundry, E self-hosted/DSGVO) → ADRs + `CLAUDE.md` → optional Projektgerüst aus dem Template-Repo. Grundlage ist eine Recherche vom August 2026 (`references/`).

## Installation

**Persönlich (alle Projekte):**
```bash
git clone https://github.com/JulesCyb/claude-skills ~/src/claude-skills
ln -s ~/src/claude-skills/ai-app-architecture ~/.claude/skills/ai-app-architecture
```
Claude Code folgt Symlinks; ein `git pull` aktualisiert den Skill für alle Projekte.

**Nur in einem Projekt:** Ordner nach `.claude/skills/ai-app-architecture/` kopieren und committen – dann hat jeder im Repo den Skill.

**Für das ganze Team:** als Plugin in einem Marketplace veröffentlichen (siehe Claude-Code-Doku "Plugins") oder Managed Settings der Organisation.

## Nutzung

- Automatisch: Claude lädt den Skill, sobald es um ein neues KI-/Agent-Projekt, Stack- oder Architekturfragen geht.
- Direkt: `/ai-app-architecture` (optional mit Stichworten: `/ai-app-architecture Kundenprojekt Azure, mehrere Mandanten`).
- Ergebnis: `docs/adr/0001-architektur.md`, `CLAUDE.md`, ggf. weitere ADRs und ein Projektgerüst.

`metadata.template_repo` in `SKILL.md` zeigt auf <https://github.com/JulesCyb/ai-app-template>.

## Struktur

```
SKILL.md                    Ablauf, Grundsätze, Verweise (wird bei Aktivierung geladen)
references/blueprints.md    Blueprints A–E, Vergleich, Wechselkriterien
references/agent-architektur.md   Backend als API, Datenzugriff, Streaming, State
references/mandanten.md     1 vs. N Mandanten, RLS-Muster, Kontext-Objekt
references/stack-2026-08.md Kurzfassung der Recherche mit Quellen
references/recherche-2026-08.md   vollständiger Recherchebericht
assets/CLAUDE.md.template   Vorlage für die Projekt-CLAUDE.md
assets/adr-template.md      ADR-Vorlage
assets/adr-0001-beispiel.md ausgefülltes Beispiel
assets/adr-0005-mobile.md   ADR-Vorlage Mobile-App (Client des Backends)
evals/evals.json            Testprompts (skill-creator-Plugin)
```

## Pflege

- Erkenntnisse aus Projekten (bessere Bibliothek, gescheiterte Entscheidung, Preisänderung) in die passende Referenzdatei schreiben.
- `metadata.version` und `metadata.stand` in `SKILL.md` anpassen, Changelog unten ergänzen.
- Nach größeren Änderungen die Testprompts laufen lassen: in Claude Code `/plugin install skill-creator@claude-plugins-official`, dann "evaluate my ai-app-architecture skill".
- Keine Kundendaten, keine Secrets in diesen Skill – nur Prinzipien und öffentliche Informationen.

## Changelog

- 1.1.0 (2026-08) – Mobile Clients: Frage 3 erweitert, Abschnitt in agent-architektur.md, ADR-Vorlage 0005, Testprompt.
- 1.0.0 (2026-08) – Erste Fassung aus der Stack-Recherche 2026-08.
