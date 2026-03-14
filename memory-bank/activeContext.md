# Active Context: Product Catalog Service

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

- **P4 linter** — ruff + mypy per `wilddog64/shopping-cart-infra/docs/plans/p4-linter-product-catalog.md`. Branch `feature/p4-linter`, PR #2 open; CI run `23095194470` green on HEAD `4a4cca64`. Copilot review requested. Ready to merge.

## Key Notes

- Flat structure (not layered) — do not refactor to services/repositories/models without team decision
- No Alembic migrations yet — uses `Base.metadata.create_all()` for dev. Production needs proper migrations.
- `.[rabbitmq]` optional dep installs pika + hvac + tenacity
