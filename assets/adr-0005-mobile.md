# ADR-0005: Mobile app as a client of the agent backend

- **Status:** proposed
- **Date:** YYYY-MM-DD
- **Deciders:** <name>
- **Skill version:** ai-app-blueprints v2.0.0 (research 2026-08)

## Context

<Why an app? Who uses it, which devices (Android/iOS/both), which native features (camera, offline, push, background), does a Next.js frontend already exist, which team?> The agent backend stays unchanged; the app is another client of the API (ADR-0001).

## Options

1. **PWA / packaged web app** (Capacitor, Trusted Web Activity) — cheapest entry, no native feel, limited device features.
2. **Expo / React Native** — same language as the web frontend, shared types/logic, AI SDK against `/api/chat`; components are not shared 1:1.
3. **Native (Kotlin/Compose, Swift/SwiftUI)** — best integration, a third language, its own maintenance; Flutter/KMP as middle roads.

## Decision

We choose **option X** because … Order: <e.g. PWA test first, then Expo>.

## Consequences for the backend (tasks)

- [ ] `AUTH_MODE=jwt`: OIDC + PKCE with <identity provider>, refresh tokens, revocation
- [ ] API contracts: `/v1/`, OpenAPI as the contract, a generated client, a deprecation rule
- [ ] Long runs as jobs with a status endpoint/push, results in the DB
- [ ] File uploads via signed URLs (tenant prefix), server-side processing
- [ ] Push (FCM/APNs): device tokens per user/tenant, no content in payloads
- [ ] Per-user rate limits; Play Integrity/App Attest only when needed

## Revisit when …

- native features are needed that the chosen option cannot deliver
- the web frontend is dropped or the team changes (TS ↔ native)
- store requirements (review, privacy declarations) change
