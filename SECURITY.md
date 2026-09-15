# Security Policy — chittytrace

## Reporting a vulnerability

Report suspected vulnerabilities privately to security@chitty.cc. Do not open a
public issue. Please allow 5 business days for an initial response.

## Secret handling

- Secrets are brokered. 1Password is retired as the credential cold source
  (commit 4a40aef); ChittySecrets (`secrets.chitty.cc`) fronting Cloudflare
  Secrets Store is the canonical path, resolved at the call site.
- Committing secret values to this repository is prohibited.
- `wrangler.jsonc` currently declares no `secrets_store_secrets` binding. The
  worker reads no secrets from the runtime environment today; the caller
  supplies the Anthropic key per request (see below).

## Current authentication posture — NOT production-grade

This section describes what the code does, not what it should do. Treat it as a
known gap, not a control.

- `_createAuthHandler` (`src/chitty-cloudflare-core.js:169-181`) treats any
  non-empty `Authorization: Bearer <value>` as authenticated. There is no
  signature, expiry, audience, or issuer check.
- `_getUserFromApiKey` (`src/chitty-cloudflare-core.js:185-187`) derives caller
  identity from the first 8 characters of the supplied key.
- `AuthService.authenticate` (`src/chitty-cloudflare-core.js:330-333`) is a stub
  that returns `{ valid: true }` unconditionally.
- `POST /api/analyze` (`src/index.js:80`) accepts an `apiKey` from the JSON
  request body and forwards it to Anthropic.
- CORS is `origins: ['*']` while the `Authorization` header is allowed
  (`src/index.js:26-29`).

No ChittyAuth integration, OAuth/PKCE flow, JWT or JWKS verification, or
Cloudflare Access (`Cf-Access-*`) handling exists in this repository. Do not
record those controls as satisfied for this service.

## Closing the gap

Wiring ChittyAuth token verification and removing the body-supplied `apiKey`
path are prerequisites for handling non-public data in this service. Until then,
deploy it only behind an external access control that does enforce identity.

## Observability

Telemetry is off per the ratified fleet OFF standard (operator decision
2026-08-16, CHITTYOS/chittyentity PR #650). The worker emits no logs or traces
to a collector, so incident reconstruction depends on Cloudflare's own request
logs.
