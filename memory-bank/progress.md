# Progress: Product Catalog Service

## Status
- **v1.5.0 IN PROGRESS** (2026-05-27) — Integration testing and Migrations.
- **v1.4.0 SHIPPED** (2026-05-27) — Resolved seed job race condition.
- **v0.3.0 SHIPPED** — Initial identity integration.

## Milestone: v1.5.0 (Integration & Migrations)
- [ ] Integration tests against real PostgreSQL (Testcontainers)
- [ ] Alembic initialization and first migration

## Milestone: v1.4.0 (Bootstrap Fix) — ARCHIVED
- [x] Add initContainer wait to seed-job.yaml
- [x] Correct Service port for health check loop
- [x] Harden initContainer with securityContext and job deadline

## Milestone: v1.3.0 (Identity) — ARCHIVED
- [x] FastAPI authentication integration
- [x] Keycloak JWKS validation
