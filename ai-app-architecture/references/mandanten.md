# Mandanten: 1 vs. N – Entscheidungspfad

Der Unterschied zwischen einem und vielen Mandanten sitzt fast komplett in der Datenschicht und der Identität. Drei Dinge von Tag 1 machen den zweiten Mandanten zu einem `INSERT` statt zu einem Rewrite.

## Immer, auch bei einem Mandanten

1. **`tenant_id` in jeder Tabelle** – auch wenn überall dieselbe steht, Embeddings eingeschlossen. Filter nicht handgeschrieben in jeder Abfrage, sondern zentral: Postgres Row-Level Security (Backend setzt pro Transaktion den Mandanten, die DB filtert) plus Repository-Schicht, durch die alle Zugriffe laufen.
2. **Kontext-Objekt statt globaler Zustand** – `user_id`, `tenant_id`, Rollen werden durch Request, Agent-Lauf, Tool und Hintergrundjob gereicht. Der Agent kennt keinen Mandanten; er ruft Tools auf, die den Kontext schon haben.
3. **Konfiguration pro Mandant** – Modellwahl, Prompts, Limits, Feature-Flags, Fremdsystem-Zugänge in einer `tenant_settings`-Tabelle (bzw. `tenants.settings jsonb`), nicht in der `.env`. Bei einem Mandanten eine Zeile – aber die Codepfade existieren.

## Entscheidungstabelle

| Bereich | Nur du / 1 Mandant | Mehrere Mandanten |
|---|---|---|
| Datenbank | Eine Postgres, `tenant_id` + RLS an, ein Mandant angelegt | Bleibt eine DB mit RLS (reicht für die meisten SaaS bis weit hoch). Schema oder DB pro Mandant nur bei vertraglicher Forderung oder wenn ein Mandant riesig wird – dann per Migration rausziehen |
| Login/Rollen | Einfaches Login, `users` und `tenants` als Tabellen trotzdem vorhanden | Onboarding (Mandant anlegen, Admin einladen), Rollen pro Mandant, SSO/OIDC über Keycloak/Zitadel/Auth0 |
| Modell-Zugang | Eigene API-Keys, EU-Region, LiteLLM oder direkt | Pro Mandant virtuelle Keys mit Budget und Rate-Limit (LiteLLM); Enterprise-Kunden wollen oft eigenes Bedrock-/Azure-Konto (BYOK) – daher Provider-Abstraktion von Anfang an |
| Vektorsuche/RAG | pgvector mit `tenant_id`-Filter | gleich, plus Index pro Mandant; erst bei sehr großen Datenmengen Partitionierung oder Qdrant mit Filter pro Mandant |
| Tools/MCP | Tools mit eigenem Kontext, Zugangsdaten zentral | Zugangsdaten pro Mandant verschlüsselt gespeichert, Tool-Aufrufe immer mit Tenant-Kontext, MCP-Server pro Mandant konfigurierbar |
| Dateien | Verzeichnis oder S3-kompatibler Speicher | gleicher Speicher, Prefix pro Mandant, signierte URLs |
| Kosten/Nutzung | Langfuse mit `tenant`-Tag | Nutzung pro Mandant tracken, Limits, später Abrechnung (Stripe) |
| Cache | kann global sein | alles Gecachte mit `tenant_id` im Schlüssel |
| Deployment | ein Docker Compose auf einem EU-Server | ein geteiltes Deployment, horizontal skaliert; getrennte Instanzen nur für Kunden, die es bezahlen |
| Audit | nicht nötig | Log: wer hat welchen Agent mit welchen Daten wann laufen lassen |

Der einzige echte Fork ist die Datenisolation – und die lässt sich vertagen, solange alles durch eine Repository-Schicht mit Tenant-Kontext geht.

## RLS-Muster (PostgreSQL)

```sql
CREATE TABLE documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id),
  title text NOT NULL,
  content text NOT NULL,
  embedding vector(1536),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX documents_tenant_idx ON documents (tenant_id);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;   -- gilt auch für den Tabellen-Owner
CREATE POLICY documents_tenant_isolation ON documents
  USING      (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

Pro Transaktion setzt das Backend den Mandanten:

```sql
SELECT set_config('app.tenant_id', :tenant_id, true);  -- true = nur für diese Transaktion
```

Fallstricke:
- **Superuser und Rollen mit `BYPASSRLS` umgehen RLS.** Der Standardnutzer des Postgres-Docker-Images ist Superuser. Die App braucht eine eigene Rolle: `CREATE ROLE app LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD '…'`, Migrationen laufen mit der Owner-Rolle.
- `current_setting('app.tenant_id', true)` liefert `NULL`, wenn nichts gesetzt ist → Policy blockt alles. Das ist gewollt: kein Kontext, keine Daten.
- Hintergrundjobs müssen den Kontext explizit setzen – sie haben keinen Request.
- Tests: pro Test einen zweiten Mandanten anlegen und prüfen, dass Abfragen ihn nicht sehen.

## Kontext-Objekt (Python)

```python
from dataclasses import dataclass, field
from uuid import UUID

@dataclass(frozen=True)
class RequestContext:
    tenant_id: UUID
    user_id: UUID
    roles: frozenset[str] = field(default_factory=frozenset)
    request_id: str = ""

    def require_role(self, role: str) -> None:
        if role not in self.roles:
            raise PermissionError(f"role {role!r} required")
```

- Entsteht einmal pro Request (aus Session/JWT) in einer FastAPI-Dependency, wird als `deps` an den PydanticAI-Agent gegeben und in jedem Tool über `ctx.deps` gelesen.
- Für Jobs: Kontext serialisiert mit dem Job speichern und beim Ausführen rekonstruieren.
- Für MCP-Server: Kontext aus dem Auth-Token der Verbindung; lokal per Umgebungsvariablen nur für Entwicklung.

## Wann Schema- oder DB-pro-Mandant

- Vertragliche Forderung ("unsere Daten physisch getrennt"), regulatorische Vorgabe, oder ein Mandant erzeugt einen Großteil der Last.
- Umsetzung: Repository-Schicht bekommt eine Verbindungs-Auflösung pro Mandant (Connection-Router); Schema bleibt identisch; Migrationen laufen über alle Mandanten-DBs. Nur machen, wenn wirklich nötig – Betriebskosten steigen mit jeder DB.
