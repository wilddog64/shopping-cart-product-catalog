# Changelog

## [Unreleased]

### Added
- `.githooks/pre-push`: pre-push hook to block accidental direct pushes from feature branches to main; bypass with `ALLOW_MAIN_PUSH=1`
- ExternalSecret resource (`k8s/base/externalsecret.yaml`) provisioning `product-catalog-secrets` from Vault — pulls DB credentials from `secret/data/postgres/products` and RabbitMQ credentials from `secret/data/rabbitmq/default`; fixes `CreateContainerConfigError` on fresh cluster deploys with ESO+Vault
- Python-based seed Job generating 1,000 products across 4 categories × 20 subcategories (50 each with deterministic UUIDs)
- GIN full-text search index on `name || description || category`; wired `?q=` query param to `GET /api/products` for search results
- Product image URLs point to MinIO via nginx proxy (`/minio/product-images/<subcategory>.jpg`); deterministic prices and quantities
- CI integration test job with real PostgreSQL service container to catch schema regressions on every PR; runs `make test-integration` with `ENVIRONMENT=sandbox`

### Fixed
- Recreate products table on schema mismatch in non-production environments — `init_db()` now detects old schema (INTEGER PK, `inventory_count`, no `currency`) and drops/recreates the table; logs warning and skips DROP when `ENVIRONMENT=production` to prevent accidental data loss
- Bump product-catalog image tag to sha-6ca5e88d to deploy init_db fix (products_search_vector function); unblocks ArgoCD sync by ensuring function exists at startup
- Move `products_search_vector` IMMUTABLE SQL function creation into `init_db()` in `database.py` so it is always present at app startup; removes function creation from PostSync job (only `CREATE INDEX IF NOT EXISTS` remains in fts-index-job.yaml); fixes 500 errors on `GET /api/products?q=...` during the ArgoCD sync window
- `src/product_catalog/routers/products.py`: add `ORDER BY id` to list query — without it, PostgreSQL returns rows in heap order (all laptops on page 1 because they were inserted first by the seed job)
- `.github/workflows/ci.yml`: bump pinned `shopping-cart-infra` SHA from `999f8d7` to `dd7496b` — old SHA referenced `trivy-action@0.30.0` which no longer resolves, blocking all image builds since PR #23 merged
- `k8s/base/service.yaml`: set ClusterIP `port` to 8082 to match frontend nginx upstream config at `/api/products → product-catalog.shopping-cart-apps.svc.cluster.local:8082`; port was 80, causing kube-proxy to drop requests and produce 504 on every API call
- `k8s/base/namespace.yaml` (deleted), `k8s/base/kustomization.yaml`: remove duplicate `Namespace/shopping-cart-apps` definition — namespace is now owned by the dedicated `shopping-cart-namespace` ArgoCD Application in k3d-manager; resolves `SharedResourceWarning` that kept this app `OutOfSync`
- Align k8s manifests with data-layer: correct DATABASE_USER, DATABASE_PASSWORD, RABBITMQ_USER, RABBITMQ_PASSWORD, fix DATABASE_HOST to postgresql-products.shopping-cart-data.svc.cluster.local, fix readiness probe path /health/ready→/health

### Changed
- Reduce deployment replicas from 2 to 1 for dev/test environment; delete HPA (`minReplicas: 2` was scaling pods back up on single-node cluster); will reintroduce in v1.1.0 EKS
- `k8s/base/deployment.yaml`: set rolling update to `maxSurge: 0` / `maxUnavailable: 1` (recreate-style) so rollouts complete on the single-node hostinger cluster instead of wedging with an unschedulable surge pod

## [0.1.0] - 2026-03-14

### Added
- FastAPI product catalog service with SQLAlchemy ORM
- Product CRUD endpoints (list, get, create, update, delete)
- OAuth2/OIDC JWT validation via Keycloak JWKS
- Security middleware: rate limiting, security headers
- RabbitMQ event publisher (InventoryUpdatedEvent)
- Prometheus metrics, health/readiness/liveness probes
- Dockerfile (multi-stage, python:3.11-slim with security upgrades)
- Kubernetes manifests (Deployment, Service, ConfigMap)
- GitHub Actions CI: ruff + mypy lint gate + build/test + Trivy + ghcr.io push
- Branch protection (1 required review + CI status check)
