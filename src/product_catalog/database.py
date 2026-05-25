"""Database connection and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models import Base, Product

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    _recreate_products_if_schema_mismatch()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION products_search_vector(
                name text,
                description text,
                category text
            )
            RETURNS tsvector LANGUAGE sql IMMUTABLE AS $$
                SELECT to_tsvector('pg_catalog.english', concat_ws(' ', name, description, category))
            $$
        """))


def _recreate_products_if_schema_mismatch() -> None:
    """Drop the products table in non-production when the schema is stale."""
    inspector = sa_inspect(engine)
    if not inspector.has_table("products"):
        return

    actual_cols = {column["name"] for column in inspector.get_columns("products")}
    expected_cols = {column.name for column in Product.__table__.columns}
    missing = expected_cols - actual_cols

    if not missing:
        return

    if settings.environment == "production":
        import logging

        logging.getLogger(__name__).warning(
            "products schema mismatch detected in production — skipping recreation; missing columns: %s",
            missing,
        )
        return

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
