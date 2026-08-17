# ADR-0005: Mobile-App als Client des Agent-Backends

- **Status:** vorgeschlagen
- **Datum:** YYYY-MM-DD
- **Entscheider:** <Name>
- **Skill-Stand:** ai-app-architecture v1.1.0 (Recherche 2026-08)

## Kontext

<Warum eine App? Wer nutzt sie, welche Geräte (Android/iOS/beide), welche nativen Features (Kamera, Offline, Push, Hintergrund), gibt es schon ein Next.js-Frontend, welches Team?> Das Agent-Backend bleibt unverändert; die App ist ein weiterer Client der API (ADR-0001).

## Optionen

1. **PWA / verpackte Web-App** (Capacitor, Trusted Web Activity) – billigster Einstieg, kein natives Gefühl, eingeschränkte Gerätefunktionen.
2. **Expo / React Native** – gleiche Sprache wie das Web-Frontend, geteilte Typen/Logik, AI SDK gegen `/api/chat`; Komponenten nicht 1:1 teilbar.
3. **Nativ (Kotlin/Compose, Swift/SwiftUI)** – beste Integration, dritte Sprache, eigene Pflege; Flutter/KMP als Zwischenwege.

## Entscheidung

Wir wählen **Option X**, weil … Reihenfolge: <z. B. erst PWA-Test, dann Expo>.

## Konsequenzen für das Backend (Aufgaben)

- [ ] `AUTH_MODE=jwt`: OIDC + PKCE mit <Identity-Provider>, Refresh-Tokens, Widerruf
- [ ] API-Verträge: `/v1/`, OpenAPI als Vertrag, generierter Client, Deprecation-Regel
- [ ] Lange Läufe als Jobs mit Status-Endpunkt/Push, Ergebnisse in DB
- [ ] Datei-Uploads über signierte URLs (Tenant-Prefix), serverseitige Verarbeitung
- [ ] Push (FCM/APNs): Gerätetokens pro Nutzer/Mandant, keine Inhalte im Payload
- [ ] Rate-Limits pro Nutzer; Play Integrity/App Attest nur bei Bedarf

## Überprüfen, wenn …

- native Features gebraucht werden, die die gewählte Option nicht liefert
- das Web-Frontend wegfällt oder das Team wechselt (TS ↔ nativ)
- Store-Anforderungen (Review, Datenschutzangaben) sich ändern
