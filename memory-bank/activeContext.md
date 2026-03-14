## CI Status (2026-03-14)

**Branch:** `feature/p4-linter` — PR [#2](https://github.com/wilddog64/shopping-cart-product-catalog/pull/2)

| Job | Status |
|---|---|
| Lint & Type Check (ruff + mypy) | ✅ run `23095114694` on commit `95fd02434ff72fafa63b0e27dcbef143ce9e8a46` (verified) |
| Lint, Test & Build | ✅ (runs after lint in the same workflow) |

Latest changes: added Ruff/Mypy config + dev deps in `pyproject.toml`, introduced a `lint` job in `.github/workflows/ci.yml`, and fixed Ruff/Mypy findings across auth, messaging, routers, and tests so the new gate is green.

---# Active Context: Product Catalog Service

## Current Status (2026-03-14)

CI green. PR #1 merged to main. Branch protection active.

## What's Implemented

- FastAPI app with lifespan handler, SQLAlchemy Product model, pydantic-settings config
- Product CRUD endpoints, health/readiness/liveness probes, Prometheus metrics
- OAuth2/OIDC JWT validation (Keycloak JWKS), security middleware (headers, rate limiting)
- RabbitMQ event publisher (InventoryUpdatedEvent etc.)
- Unit tests: test_auth.py, test_auth_integration.py, test_security.py, test_security_middleware.py
- Dockerfile, k8s/base manifests, GitHub Actions ci.yml

## CI History

- **fix/ci-stabilization PR #1** — merged 2026-03-14. Fixed: Dockerfile security upgrades.
- **Branch protection** — 1 review + CI required, enforce_admins: false

## Active Task

- **P4 linter** — ruff + mypy per `wilddog64/shopping-cart-infra/docs/plans/p4-linter-product-catalog.md`. Branch `feature/p4-linter`, PR #2 open; CI run `23095114694` succeeded on commit `95fd02434ff72fafa63b0e27dcbef143ce9e8a46`.

## Key Notes

- Flat structure (not layered) — do not refactor to services/repositories/models without team decision
- No Alembic migrations yet — uses `Base.metadata.create_all()` for dev. Production needs proper migrations.
- `.[rabbitmq]` optional dep installs pika + hvac + tenacity
