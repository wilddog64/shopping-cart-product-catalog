# Changelog

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
