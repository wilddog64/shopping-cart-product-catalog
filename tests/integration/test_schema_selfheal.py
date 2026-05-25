"""Integration test: schema self-heal on stale products table."""

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

from product_catalog import database as db_module


@pytest.mark.integration
def test_init_db_recreates_stale_products_table():
    """init_db() must drop and recreate products when old schema is present."""
    with db_module.engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
        conn.execute(text("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                price NUMERIC(10,2) NOT NULL,
                inventory_count INTEGER NOT NULL DEFAULT 0
            )
        """))

    db_module.init_db()

    inspector = sa_inspect(db_module.engine)
    cols = {c["name"] for c in inspector.get_columns("products")}
    assert "currency" in cols
    assert "quantity" in cols
    assert "inventory_count" not in cols
