# ChittyTrace Charter

## Classification
- **Canonical URI**: `chittycanon://core/services/chittytrace`
- **Tier**: 4 (Domain)
- **Organization**: chittyapps
- **Domain**: chittytrace.chitty.cc

## Mission

Evidence tracking and litigation support platform with document processing. Provides chain-of-custody tracking and document analysis.

## Scope

### IS Responsible For
- Evidence tracking, litigation support, document processing, chain-of-custody management

### IS NOT Responsible For
- Identity generation (ChittyID)
- Token provisioning (ChittyAuth)

## Dependencies

| Type | Service | Purpose |
|------|---------|---------|
| Upstream | ChittyAuth | Authentication |

## API Contract

**Base URL**: https://chittytrace.chitty.cc

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Service health |

## Ownership

| Role | Owner |
|------|-------|
| Service Owner | chittyapps |

## Compliance

- [ ] Registered in ChittyRegister
- [ ] Health endpoint operational at /health
- [ ] CLAUDE.md present
- [ ] CHARTER.md present
- [ ] CHITTY.md present

---
*Charter Version: 1.0.0 | Last Updated: 2026-02-21*