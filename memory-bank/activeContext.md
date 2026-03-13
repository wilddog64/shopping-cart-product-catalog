## CI Status (as of 2026-03-13)

**Branch:** `fix/ci-stabilization` — PR #1 open

| Job | Status |
|---|---|
| Lint, Test & Build | ✅ pass |

**CI is green. PR #1 ready to merge.**

Fix applied: added `apt-get upgrade -y` immediately after `FROM python:3.11-slim`
in Dockerfile to resolve Trivy HIGH/CRITICAL CVEs.

---# Active Context: Product Catalog Service

## Current Status

Active development. The core FastAPI application, Product model, configuration, and security/auth layers are implemented. Unit tests for authentication and security middleware are in place. The service has a complete Kubernetes manifest set with ArgoCD integration.

## Implemented Features

- FastAPI application with lifespan handler (`init_db()` on startup)
- `Product` SQLAlchemy model with all fields (id, sku, name, description, price, currency, quantity, category, is_active, image_url, created_at, updated_at)
- `Settings` via pydantic-settings with `get_settings()` cached singleton
- `database.py` with SQLAlchemy engine and session factory
- `events.py` with RabbitMQ event classes (InventoryUpdatedEvent, etc.) and common envelope format
- `messaging.py` RabbitMQ publisher
- `auth.py` — OAuth2/OIDC JWT validation with Keycloak JWKS
- `security.py` — security middleware (headers, rate limiting) via `setup_security(app)`
- `routers/products.py` — product CRUD endpoints
- `routers/health.py` — health check endpoints
- Prometheus metrics ASGI mount at `/metrics`
- Unit tests: `test_auth.py`, `test_auth_integration.py`, `test_security.py`, `test_security_middleware.py`

## Active Development Notes

### Flat vs Layered Structure
The `docs/architecture/README.md` describes a future structure with `services/`, `repositories/`, `models/` subdirectories. The current implementation is flat. New code should match the **current flat structure** unless the team explicitly decides to refactor to the layered approach.

### Alembic Setup
Alembic is in the dependencies and Makefile has `db-migrate`/`db-migrate-create` targets. However, no `alembic/` directory is visible in the file listing. The `database.py` likely uses `Base.metadata.create_all()` in `init_db()` for now (SQLAlchemy auto-create), which is suitable for development but not production. For production, Alembic migrations should be properly initialized.

### RabbitMQ Client Library
The `.[rabbitmq]` optional dependency installs `pika`, `hvac`, and `tenacity`. A separate `rabbitmq-client-library` Python package is referenced for local installation:
```bash
pip install -e "../rabbitmq-client-library/python"
```
This library provides higher-level abstractions over pika with Vault integration.

### No GitHub Actions Workflows Visible
Unlike the Payment Service which has explicit workflow files, no `.github/workflows/` files are visible. The Makefile has `ci-test` and `ci-build` targets that could be used by any CI system.

## CI Blocker — OPEN (2026-03-11)

**Failing since:** 2026-03-09
**Failing job:** `Publish / build-push` → Trivy scanner installation

**Error:** Same as shopping-cart-basket (identical shared reusable workflow at same pinned commit).

```
aquasecurity/trivy info found version: 0.60.0 for v0.60.0/Linux/64bit
##[error]Process completed with exit code 1.
```

**Root cause:** Custom Trivy install script in `shopping-cart-infra` reusable workflow fails during binary download.

**Fix (shared with shopping-cart-basket — fix once in infra repo):**
Replace custom script with `aquasecurity/trivy-action@0.30.0` in `shopping-cart-infra/.github/workflows/build-push-deploy.yml`;
then update the pinned commit hash in this repo's caller workflow.

**Priority:** P1 — assigned to v0.8.0 milestone. See `k3d-manager/docs/issues/2026-03-11-shopping-cart-ci-failures.md`.

## Integration Points

- **Product data consumer**: Basket Service clients read product details from here when building carts (though the Basket Service does not call this API — the frontend client does)
- **Inventory events consumer**: Order Service may consume `inventory.*` events for fulfillment tracking
- **PostgreSQL**: `products` database; K8s: `shopping-cart-data` namespace
- **RabbitMQ**: exchange `events`; routing keys `inventory.updated`, `inventory.low`, `inventory.reserved`
- **Keycloak**: JWKS at `OAUTH2_ISSUER_URI/protocol/openid-connect/certs`; 5-minute JWKS cache
- **Vault**: Optional dynamic RabbitMQ credentials at `VAULT_RABBITMQ_PATH/creds/VAULT_ROLE`

## Currently Implemented Tests

`tests/unit/`:
- `test_auth.py` — JWT auth unit tests
- `test_auth_integration.py` — auth integration tests (may mock Keycloak)
- `test_security.py` — security configuration tests
- `test_security_middleware.py` — middleware behavior tests

`tests/integration/`: directory exists but no test files visible — integration tests may be pending.

## API Endpoints Active

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/products` | Optional | List products with pagination/filtering |
| GET | `/api/products/{id}` | Optional | Get product by ID |
| GET | `/api/products/sku/{sku}` | Optional | Get product by SKU |
| POST | `/api/products` | Required (catalog-admin) | Create product |
| PATCH | `/api/products/{id}` | Required (catalog-admin) | Update product |
| DELETE | `/api/products/{id}` | Required (catalog-admin) | Soft-delete product |
| POST | `/api/products/{id}/inventory` | Required (catalog-admin) | Update inventory |
| GET | `/health` | Public | Health check |
| GET | `/ready` | Public | Readiness probe |
| GET | `/live` | Public | Liveness probe |
| GET | `/metrics` | Public | Prometheus metrics |
