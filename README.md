# Shopping Cart Product Catalog Service

Product catalog microservice for the Shopping Cart platform with RabbitMQ integration for event-driven architecture.

## Overview

The Product Catalog Service handles:
- Product CRUD operations
- Inventory management
- Event publishing for inventory changes
- Product search and filtering

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Product Catalog Service                     │
├─────────────────────────────────────────────────────────────┤
│  REST API           │  Event Publisher    │  Event Consumer │
│  - GET /products    │  - inventory.updated│  - order.*      │
│  - POST /products   │  - inventory.low    │                 │
│  - PATCH /products  │  - inventory.reserved                 │
│  - POST /inventory  │                     │                 │
├─────────────────────────────────────────────────────────────┤
│                     PostgreSQL                               │
│                     (products)                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │    RabbitMQ     │
                    │  events exchange │
                    └─────────────────┘
```

## Events Published

| Event | Routing Key | Description |
|-------|-------------|-------------|
| InventoryUpdatedEvent | `inventory.updated` | Inventory quantity changed |
| InventoryLowEvent | `inventory.low` | Stock below threshold |
| InventoryReservedEvent | `inventory.reserved` | Stock reserved for order |

See [Message Schemas](../shopping-cart-infra/docs/message-schemas.md) for event format details.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- RabbitMQ 3.12+ (via shopping-cart-infra)
- HashiCorp Vault (optional, for dynamic credentials)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package with dev dependencies
pip install -e ".[dev,rabbitmq]"
```

### 2. Run with Docker Compose (Development)

```bash
docker-compose up -d
python -m product_catalog.main
```

### 3. Run with uvicorn directly

```bash
uvicorn product_catalog.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | products | Database name |
| `DB_USERNAME` | postgres | Database username |
| `DB_PASSWORD` | postgres | Database password |
| `RABBITMQ_HOST` | localhost | RabbitMQ host |
| `RABBITMQ_PORT` | 5672 | RabbitMQ AMQP port |
| `VAULT_ENABLED` | false | Enable Vault integration |
| `VAULT_ADDR` | http://localhost:8200 | Vault address |
| `VAULT_ROLE` | product-publisher | Vault role for RabbitMQ |

## API Endpoints

### List Products
```bash
GET /api/products?page=1&page_size=20&category=electronics&active_only=true
```

### Get Product by ID
```bash
GET /api/products/{product_id}
```

### Get Product by SKU
```bash
GET /api/products/sku/{sku}
```

### Create Product
```bash
POST /api/products
Content-Type: application/json

{
  "sku": "WIDGET-001",
  "name": "Premium Widget",
  "description": "A high-quality widget",
  "price": 29.99,
  "currency": "USD",
  "quantity": 100,
  "category": "electronics"
}
```

### Update Product
```bash
PATCH /api/products/{product_id}
Content-Type: application/json

{
  "price": 34.99,
  "quantity": 150
}
```

### Update Inventory
```bash
POST /api/products/{product_id}/inventory
Content-Type: application/json

{
  "quantity_change": -5,
  "reason": "Order fulfillment"
}
```

### Delete Product (soft delete)
```bash
DELETE /api/products/{product_id}
```

## Health & Metrics

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check with database status |
| `/ready` | Kubernetes readiness probe |
| `/live` | Kubernetes liveness probe |
| `/metrics` | Prometheus metrics |

## Development

### Run Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests (requires Docker)
pytest tests/integration -v

# With coverage
pytest --cov=product_catalog --cov-report=term-missing
```

### Code Style

```bash
# Format code
black src tests
isort src tests

# Type checking
mypy src

# Linting
ruff check src tests
```

## Project Structure

```
shopping-cart-product-catalog/
├── src/
│   └── product_catalog/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       ├── database.py         # Database connection
│       ├── events.py           # RabbitMQ event definitions
│       ├── main.py             # FastAPI application
│       ├── models.py           # SQLAlchemy models
│       ├── schemas.py          # Pydantic schemas
│       └── routers/
│           ├── health.py       # Health check endpoints
│           └── products.py     # Product CRUD endpoints
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

## Related Repositories

- [shopping-cart-infra](../shopping-cart-infra) - Kubernetes infrastructure, RabbitMQ cluster
- [shopping-cart-order](../shopping-cart-order) - Order processing service
- [rabbitmq-client-library](../rabbitmq-client-library) - Python RabbitMQ client library

## License

Apache 2.0
