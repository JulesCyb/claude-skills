# Tenancy: 1 vs. N — the decision path

The difference between one tenant and many sits almost entirely in the data layer and identity. Three things from day one turn the second tenant into an `INSERT` instead of a rewrite.

## Always, even with a single tenant

1. **`tenant_id` in every table** — even if it is the same everywhere, embeddings included. Do not hand-write the filter into every query; centralize it: Postgres Row-Level Security (the backend sets the tenant per transaction, the DB filters) plus a repository layer all access goes through.
2. **A context object instead of global state** — `user_id`, `tenant_id`, roles are passed through request, agent run, tool, and background job. The agent knows no tenant; it calls tools that already carry the context.
3. **Per-tenant configuration** — model choice, prompts, limits, feature flags, third-party credentials in a `tenant_settings` table (or `tenants.settings jsonb`), not in `.env`. With one tenant that is one row — but the code paths exist.

## Decision table

| Area | Just you / 1 tenant | Multiple tenants |
|---|---|---|
| Database | one Postgres, `tenant_id` + RLS on, one tenant created | stays one DB with RLS (enough for most SaaS well into scale). Schema or DB per tenant only on contractual demand or when one tenant dominates the load — then extract via migration |
| Login/roles | simple login; `users` and `tenants` tables exist anyway | onboarding (create tenant, invite admin), per-tenant roles, SSO/OIDC via Keycloak/Zitadel/Auth0 |
| Model access | own API keys, EU region, LiteLLM or direct | virtual keys per tenant with budget and rate limit (LiteLLM); enterprise clients often want their own Bedrock/Azure account (BYOK) — hence provider abstraction from the start |
| Vector search/RAG | pgvector with a `tenant_id` filter | same, plus an index per tenant; only at very large volumes partitioning or Qdrant with per-tenant filters |
| Tools/MCP | tools with own context, credentials central | per-tenant credentials stored encrypted, tool calls always with tenant context, MCP servers configurable per tenant |
| Files | a directory or S3-compatible storage | same storage, per-tenant prefix, signed URLs |
| Costs/usage | Langfuse with a `tenant` tag | track usage per tenant, limits, later billing (Stripe) |
| Cache | can be global | everything cached carries the `tenant_id` in its key |
| Deployment | one Docker Compose on one EU server | one shared deployment, scaled horizontally; separate instances only for clients who pay for them |
| Audit | not needed | log: who ran which agent with which data and when |

The only real fork is data isolation — and it can be deferred as long as everything goes through a repository layer with tenant context.

## RLS pattern (PostgreSQL)

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
ALTER TABLE documents FORCE ROW LEVEL SECURITY;   -- applies to the table owner too
CREATE POLICY documents_tenant_isolation ON documents
  USING      (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

Per transaction, the backend sets the tenant:

```sql
SELECT set_config('app.tenant_id', :tenant_id, true);  -- true = this transaction only
```

Pitfalls:
- **Superusers and roles with `BYPASSRLS` bypass RLS.** The default user of the Postgres Docker image is a superuser. The app needs its own role: `CREATE ROLE app LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD '…'`; migrations run as the owner role.
- `current_setting('app.tenant_id', true)` returns `NULL` when nothing is set → the policy blocks everything. That is intentional: no context, no data.
- Background jobs must set the context explicitly — they have no request.
- Tests: create a second tenant per test and verify queries cannot see it.

## Context object (Python)

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

- Created once per request (from session/JWT) in a FastAPI dependency, passed to the PydanticAI agent as `deps`, and read in every tool via `ctx.deps`.
- For jobs: serialize the context with the job and reconstruct it on execution.
- For MCP servers: context from the connection's auth token; environment variables only for local development.

## When schema- or DB-per-tenant

- A contractual demand ("our data physically separated"), a regulatory requirement, or one tenant generating most of the load.
- Implementation: the repository layer gets per-tenant connection resolution (a connection router); the schema stays identical; migrations run across all tenant DBs. Only do it when truly needed — operating costs grow with every DB.
